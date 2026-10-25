import math
import struct

import xbmcvfs

from bossanova808.logger import Logger

# Degrees of rotation that Amlogic's amcodec hardware decoder mishandles - see project notes.
# 180 degrees doesn't scramble width/height the same way and isn't affected.
BROKEN_ROTATIONS = (90, 270)

# AVI video codec FourCCs confirmed to hang amcodec hardware decode outright (playback never
# starts - onAVStarted never fires) rather than mis-render, unlike the rotation issue above.
# Currently just MJPEG (common in old point-and-shoot camera .avi files); add more here if other
# codecs are found to have the same problem.
BROKEN_AVI_CODECS = ("MJPG",)

# AVI video codec FourCCs that are always interlaced (DV camcorder footage)
INTERLACED_AVI_CODECS = ("DVSD", "DVSL", "DVHD", "DV25", "DV50", "DVCP", "CDVC")

MP4_EXTENSIONS = ('.mp4', '.m4v', '.mov', '.3gp')
MKV_EXTENSIONS = ('.mkv', '.mk3d', '.webm')
AVI_EXTENSIONS = ('.avi',)

_BOX_HEADER_SIZE = 8
# tkhd payload layout (ISO/IEC 14496-12): version+flags, then times/track id/duration (length
# depends on version), then 8 bytes reserved, then layer/alternate_group/volume/reserved, then the
# 9-entry (36 byte) display matrix, then the width and height as 16.16 fixed point.
_TKHD_VERSION0_HEADER = 4 + 20 + 8 + 8
_TKHD_VERSION1_HEADER = 4 + 32 + 8 + 8
_MATRIX_SIZE = 36
# Where a video sample entry's child boxes (avcC, fiel...) start, from the end of its box header
_VISUAL_SAMPLE_ENTRY_SIZE = 78

# H.264 profiles whose SPS carries chroma/bit depth/scaling list fields before the frame fields
_H264_HIGH_PROFILES = (100, 110, 122, 244, 44, 83, 86, 118, 128, 138, 139, 134, 135)

# Matroska element IDs
_MKV_SEGMENT = 0x18538067
_MKV_TRACKS = 0x1654AE6B
_MKV_CLUSTER = 0x1F43B675
_MKV_TRACK_ENTRY = 0xAE
_MKV_TRACK_TYPE = 0x83
_MKV_CODEC_ID = 0x86
_MKV_CODEC_PRIVATE = 0x63A2
_MKV_VIDEO = 0xE0
_MKV_PIXEL_WIDTH = 0xB0
_MKV_PIXEL_HEIGHT = 0xBA
_MKV_FLAG_INTERLACED = 0x9A
_MKV_TRACK_TYPE_VIDEO = 1


class _Bits:
    """
    Minimal bit reader (with Exp-Golomb) for parsing an H.264 SPS. Reading past the end raises IndexError.
    """

    def __init__(self, data):
        self.data = data
        self.pos = 0

    def u(self, bits=1):
        value = 0
        for _ in range(bits):
            value = (value << 1) | ((self.data[self.pos >> 3] >> (7 - (self.pos & 7))) & 1)
            self.pos += 1
        return value

    def ue(self):
        zeros = 0
        while self.u() == 0:
            zeros += 1
            if zeros > 32:
                raise ValueError('bad Exp-Golomb code')
        return (1 << zeros) - 1 + self.u(zeros)

    def se(self):
        k = self.ue()
        return (k + 1) // 2 if k & 1 else -(k // 2)


def _sps_interlaced(sps):
    """
    Whether an H.264 SPS says the stream may be interlaced (frame_mbs_only_flag is 0). Note this
    flags interlaced-capable coding, so a broadcast 1080i stream is caught, and so is the odd
    progressive stream coded that way.

    :param sps: the SPS NAL unit, including its 1-byte NAL header
    :return: True/False, or None if it couldn't be parsed
    """
    rbsp = sps[1:].replace(b'\x00\x00\x03', b'\x00\x00')
    try:
        bits = _Bits(rbsp)
        profile = bits.u(8)
        bits.u(16)  # constraint flags, level
        bits.ue()  # sps id
        if profile in _H264_HIGH_PROFILES:
            chroma_format = bits.ue()
            if chroma_format == 3:
                bits.u()
            bits.ue()  # bit depth luma
            bits.ue()  # bit depth chroma
            bits.u()  # transform bypass
            if bits.u():  # scaling matrix present
                for i in range(8 if chroma_format != 3 else 12):
                    if bits.u():
                        last = next_scale = 8
                        for _ in range(16 if i < 6 else 64):
                            if next_scale:
                                next_scale = (last + bits.se() + 256) % 256
                            last = next_scale or last
        bits.ue()  # log2_max_frame_num
        poc_type = bits.ue()
        if poc_type == 0:
            bits.ue()
        elif poc_type == 1:
            bits.u()
            bits.se()
            bits.se()
            for _ in range(bits.ue()):
                bits.se()
        bits.ue()  # max_num_ref_frames
        bits.u()  # gaps_in_frame_num
        bits.ue()  # width in macroblocks
        bits.ue()  # height in map units
        return not bits.u()
    except (IndexError, ValueError):
        return None


def _avcc_interlaced(avcc):
    """
    :param avcc: the payload of an avcC box (or an MKV H.264 CodecPrivate, which is the same thing)
    :return: whether the SPS inside it says interlaced - True/False, or None if it couldn't be read
    """
    if len(avcc) < 9 or avcc[0] != 1 or avcc[5] & 0x1f == 0:
        return None
    length = struct.unpack('>H', avcc[6:8])[0]
    return _sps_interlaced(avcc[8:8 + length])


# MP4 / MOV ###########################################################################################

def _read_box_header(f):
    """
    Read one ISO-BMFF box header at the current file position.

    :param f: an open xbmcvfs.File
    :return: (box_type, payload_size, header_size), with the file left positioned at the start of
        the box's payload, or None at end of file
    """
    header = bytes(f.readBytes(_BOX_HEADER_SIZE))
    if len(header) < _BOX_HEADER_SIZE:
        return None
    size, box_type = struct.unpack('>I4s', header)
    box_type = box_type.decode('ascii', errors='replace')
    header_size = _BOX_HEADER_SIZE
    if size == 1:
        large = bytes(f.readBytes(8))
        if len(large) < 8:
            return None
        size = struct.unpack('>Q', large)[0]
        header_size += 8
    return box_type, size, header_size


def _boxes(f, start, end):
    """
    Walk the sibling boxes between two file offsets, seeking over their payloads - large payloads
    (e.g. mdat) are never read.

    :return: yields (box_type, payload_start, payload_end)
    """
    pos = start
    while pos + _BOX_HEADER_SIZE <= end:
        f.seek(pos, 0)
        header = _read_box_header(f)
        if header is None:
            return
        box_type, size, header_size = header
        box_end = end if size == 0 else pos + size
        if box_end <= pos or box_end > end:
            box_end = end
        yield box_type, pos + header_size, box_end
        pos = box_end


def _find_box(f, start, end, *path):
    """
    :return: (payload_start, payload_end) of the box found by following a path of nested box types,
        or None
    """
    for name in path:
        for box_type, payload_start, payload_end in _boxes(f, start, end):
            if box_type == name:
                start, end = payload_start, payload_end
                break
        else:
            return None
    return start, end


def _rotation_from_matrix(matrix_bytes):
    """
    Work out the rotation a QuickTime/MP4 display matrix represents, the same way ffprobe does
    (atan2 of the b/a components of the 2x2 rotation part of the matrix).

    :param matrix_bytes: the 36-byte tkhd matrix (9 x 32-bit fixed-point values)
    :return: rotation in degrees (0/90/180/270)
    """
    a = struct.unpack('>i', matrix_bytes[0:4])[0] / 65536.0
    b = struct.unpack('>i', matrix_bytes[4:8])[0] / 65536.0
    return round(math.degrees(math.atan2(b, a))) % 360


def _stsd_interlaced(f, start, end):
    """
    Whether a track's sample description says its video is interlaced - a QuickTime 'fiel' box, or
    an H.264 avcC box whose SPS says so.

    :return: True/False, or None if there's nothing to go on
    """
    # Skip version/flags and the entry count - only the first sample entry matters
    for _, entry_start, entry_end in _boxes(f, start + 8, end):
        for box_type, payload_start, payload_end in _boxes(f, entry_start + _VISUAL_SAMPLE_ENTRY_SIZE, entry_end):
            f.seek(payload_start, 0)
            if box_type == 'fiel':
                return bytes(f.readBytes(1)) == b'\x02'
            if box_type == 'avcC':
                return _avcc_interlaced(bytes(f.readBytes(min(payload_end - payload_start, 1024))))
        return None
    return None


def _read_track(f, start, end):
    """
    :return: what a 'trak' box tells us: handler ('vide' etc.), rotation, width, height, interlaced
    """
    track = {}
    tkhd = _find_box(f, start, end, 'tkhd')
    if tkhd:
        f.seek(tkhd[0], 0)
        payload = bytes(f.readBytes(tkhd[1] - tkhd[0]))
        offset = _TKHD_VERSION1_HEADER if payload and payload[0] == 1 else _TKHD_VERSION0_HEADER
        if len(payload) >= offset + _MATRIX_SIZE + 8:
            track['rotation'] = _rotation_from_matrix(payload[offset:offset + _MATRIX_SIZE])
            width, height = struct.unpack('>II', payload[offset + _MATRIX_SIZE:offset + _MATRIX_SIZE + 8])
            track['width'], track['height'] = width >> 16, height >> 16

    mdia = _find_box(f, start, end, 'mdia')
    if mdia:
        hdlr = _find_box(f, mdia[0], mdia[1], 'hdlr')
        if hdlr:
            # version/flags, pre_defined, then the handler type
            f.seek(hdlr[0] + 8, 0)
            track['handler'] = bytes(f.readBytes(4)).decode('ascii', errors='replace')
        stsd = _find_box(f, mdia[0], mdia[1], 'minf', 'stbl', 'stsd')
        if stsd:
            track['interlaced'] = _stsd_interlaced(f, stsd[0], stsd[1])
    return track


def _probe_mp4(f, file_size):
    """
    Facts about an MP4/MOV file's video track. Cameras/phones frequently don't "fast start" their
    files (moov at the end, after mdat), so this scans top-level boxes rather than assuming moov
    comes first.
    """
    moov = _find_box(f, 0, file_size, 'moov')
    if not moov:
        return None
    for box_type, start, end in _boxes(f, moov[0], moov[1]):
        if box_type == 'trak':
            track = _read_track(f, start, end)
            if track.get('handler') == 'vide':
                return {'rotation': track.get('rotation'), 'width': track.get('width'),
                        'height': track.get('height'), 'interlaced': bool(track.get('interlaced'))}
    return None


# Matroska ############################################################################################

def _read_vint(f, keep_marker):
    """
    Read an EBML variable-length integer (an element ID keeps its length marker bits, a size doesn't).

    :return: (value, length in bytes), or None at end of file / if malformed
    """
    first = bytes(f.readBytes(1))
    if not first:
        return None
    length, mask = 1, 0x80
    while length <= 8 and not first[0] & mask:
        length += 1
        mask >>= 1
    if length > 8:
        return None
    value = first[0] if keep_marker else first[0] & (mask - 1)
    rest = bytes(f.readBytes(length - 1))
    if len(rest) != length - 1:
        return None
    for byte in rest:
        value = (value << 8) | byte
    return value, length


def _elements(f, start, end):
    """
    Walk the sibling EBML elements between two file offsets.

    :return: yields (element_id, payload_start, payload_end)
    """
    pos = start
    while pos < end:
        f.seek(pos, 0)
        ident = _read_vint(f, True)
        size = _read_vint(f, False)
        if ident is None or size is None:
            return
        payload_start = pos + ident[1] + size[1]
        unknown_size = size[0] == (1 << (7 * size[1])) - 1
        payload_end = end if unknown_size else min(payload_start + size[0], end)
        yield ident[0], payload_start, payload_end
        pos = payload_end


def _mkv_bytes(f, start, end, limit=1024):
    f.seek(start, 0)
    return bytes(f.readBytes(min(end - start, limit)))


def _mkv_uint(f, start, end):
    return int.from_bytes(_mkv_bytes(f, start, end, 8), 'big')


def _mkv_video_facts(f, start, end):
    for ident, entry_start, entry_end in _elements(f, start, end):
        if ident != _MKV_TRACK_ENTRY:
            continue
        entry = {}
        for element, payload_start, payload_end in _elements(f, entry_start, entry_end):
            if element == _MKV_TRACK_TYPE:
                entry['type'] = _mkv_uint(f, payload_start, payload_end)
            elif element == _MKV_CODEC_ID:
                entry['codec'] = _mkv_bytes(f, payload_start, payload_end).decode('ascii', errors='replace')
            elif element == _MKV_CODEC_PRIVATE:
                entry['private'] = _mkv_bytes(f, payload_start, payload_end)
            elif element == _MKV_VIDEO:
                for video_element, video_start, video_end in _elements(f, payload_start, payload_end):
                    if video_element == _MKV_PIXEL_WIDTH:
                        entry['width'] = _mkv_uint(f, video_start, video_end)
                    elif video_element == _MKV_PIXEL_HEIGHT:
                        entry['height'] = _mkv_uint(f, video_start, video_end)
                    elif video_element == _MKV_FLAG_INTERLACED:
                        entry['flag'] = _mkv_uint(f, video_start, video_end)
        if entry.get('type') != _MKV_TRACK_TYPE_VIDEO:
            continue

        # The container's flag is 1 for interlaced and 2 for progressive; 0 (or absent) means it
        # doesn't know, so fall back to what the H.264 SPS says
        flag = entry.get('flag', 0)
        if flag:
            interlaced = flag == 1
        elif entry.get('codec') == 'V_MPEG4/ISO/AVC':
            interlaced = bool(_avcc_interlaced(entry.get('private', b'')))
        else:
            interlaced = False
        return {'rotation': None, 'width': entry.get('width'), 'height': entry.get('height'), 'interlaced': interlaced}
    return None


def _probe_mkv(f, file_size):
    """
    Facts about a Matroska file's video track. Tracks always come before the first Cluster.
    """
    for ident, start, end in _elements(f, 0, file_size):
        if ident != _MKV_SEGMENT:
            continue
        for segment_ident, tracks_start, tracks_end in _elements(f, start, end):
            if segment_ident == _MKV_TRACKS:
                return _mkv_video_facts(f, tracks_start, tracks_end)
            if segment_ident == _MKV_CLUSTER:
                return None
    return None


# AVI #################################################################################################

def _riff_chunks(f, start, end):
    """
    Walk the sibling RIFF chunks between two file offsets.

    :return: yields (fourcc, payload_start, payload_end)
    """
    pos = start
    while pos + 8 <= end:
        f.seek(pos, 0)
        header = bytes(f.readBytes(8))
        if len(header) < 8:
            return
        fourcc, size = struct.unpack('<4sI', header)
        yield fourcc, pos + 8, pos + 8 + size
        pos += 8 + size + (size & 1)


def _probe_avi(f, file_size):
    """
    Facts about an AVI file, from its header chunks only ('hdrl' always precedes the actual, often
    huge, media payload in 'movi', which is never reached).
    """
    f.seek(0, 0)
    header = bytes(f.readBytes(12))
    if header[0:4] != b'RIFF' or header[8:12] != b'AVI ':
        return None

    facts = {}
    for fourcc, start, end in _riff_chunks(f, 12, file_size):
        if fourcc != b'LIST':
            continue
        f.seek(start, 0)
        list_type = bytes(f.readBytes(4))
        if list_type == b'movi':
            break
        if list_type != b'hdrl':
            continue
        for header_fourcc, header_start, header_end in _riff_chunks(f, start + 4, end):
            if header_fourcc == b'avih':
                # main header: width and height are the 9th and 10th DWORDs
                f.seek(header_start + 32, 0)
                dimensions = bytes(f.readBytes(8))
                if len(dimensions) == 8:
                    facts['width'], facts['height'] = struct.unpack('<II', dimensions)
            elif header_fourcc == b'LIST':
                f.seek(header_start, 0)
                if bytes(f.readBytes(4)) != b'strl':
                    continue
                for stream_fourcc, stream_start, _ in _riff_chunks(f, header_start + 4, header_end):
                    if stream_fourcc == b'strh' and 'avi_codec' not in facts:
                        f.seek(stream_start, 0)
                        stream_header = bytes(f.readBytes(8))
                        if stream_header[0:4] == b'vids':
                            facts['avi_codec'] = stream_header[4:8].decode('ascii', errors='replace')
        break

    if 'avi_codec' not in facts and 'width' not in facts:
        return None
    facts['interlaced'] = facts.get('avi_codec', '').upper() in INTERLACED_AVI_CODECS
    return facts


# #####################################################################################################

def probe_file(file_path):
    """
    Read what we can about a video file from its container headers, without downloading the whole
    file - only the headers are read. Dispatches by file extension, since each container format
    needs entirely different parsing.

    The facts, any of which may be missing or None when the container doesn't say:
        rotation - degrees (0/90/180/270), MP4/MOV only
        avi_codec - the video codec's FourCC, AVI only
        width, height - the video's size in pixels
        interlaced - best effort: DV AVI, the Matroska interlaced flag, an H.264 SPS or QuickTime
            'fiel' box saying so (False if the file doesn't say)

    :param file_path: full path/URL of the video file (any Kodi VFS-supported source, e.g. smb://)
    :return: a dict of facts (empty for a file type we don't read), or None if reading the file
        or its headers failed
    """
    lower = file_path.lower()
    if lower.endswith(MP4_EXTENSIONS):
        probe = _probe_mp4
    elif lower.endswith(MKV_EXTENSIONS):
        probe = _probe_mkv
    elif lower.endswith(AVI_EXTENSIONS):
        probe = _probe_avi
    else:
        return {}

    f = xbmcvfs.File(file_path)
    try:
        file_size = f.size()
        if file_size <= 0:
            return None
        return probe(f, file_size)
    except Exception as e:
        Logger.warning(f"probe_file: could not read [{file_path}]: {e}")
        return None
    finally:
        f.close()
