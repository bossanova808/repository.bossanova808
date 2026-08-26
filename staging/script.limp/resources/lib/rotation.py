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

_BOX_HEADER_SIZE = 8
# tkhd payload layout (ISO/IEC 14496-12): version+flags, then times/track id/duration (length
# depends on version), then 8 bytes reserved, then layer/alternate_group/volume/reserved, then the
# 9-entry (36 byte) display matrix we actually want.
_TKHD_VERSION0_HEADER = 4 + 20 + 8 + 8
_TKHD_VERSION1_HEADER = 4 + 32 + 8 + 8
_MATRIX_SIZE = 36


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


def _find_child_box(f, box_type, parent_end):
    """
    Scan sibling boxes from the current file position (up to parent_end) for one matching
    box_type, leaving the file positioned at the start of its payload if found. Large payloads
    (e.g. mdat) are skipped over with a seek, never read.

    :return: payload size in bytes, or None if not found
    """
    while f.tell() < parent_end:
        header = _read_box_header(f)
        if header is None:
            return None
        this_type, size, header_size = header
        payload_size = (size - header_size) if size else (parent_end - f.tell())
        if this_type == box_type:
            return payload_size
        f.seek(f.tell() + payload_size, 0)
    return None


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


def get_rotation(file_path):
    """
    Read the rotation (0/90/180/270) embedded in an MP4/MOV file's tkhd display matrix, without
    downloading the whole file - only box headers (and the small tkhd box itself) are read; large
    payloads (e.g. mdat) are skipped over with a seek. Cameras/phones frequently don't "fast start"
    their files (moov at the end, after mdat), so this scans top-level boxes rather than assuming
    moov comes first.

    :param file_path: full path/URL of the video file (any Kodi VFS-supported source, e.g. smb://)
    :return: rotation in degrees (0/90/180/270), or None if it couldn't be determined
    """
    f = xbmcvfs.File(file_path)
    try:
        file_size = f.size()
        if file_size <= 0:
            return None

        f.seek(0, 0)
        moov_size = None
        while f.tell() < file_size:
            header = _read_box_header(f)
            if header is None:
                break
            box_type, size, header_size = header
            payload_size = (size - header_size) if size else (file_size - f.tell())
            if box_type == 'moov':
                moov_size = payload_size
                break
            f.seek(f.tell() + payload_size, 0)

        if moov_size is None:
            return None

        moov_end = f.tell() + moov_size

        # A moov can contain multiple trak boxes (video, audio, ...) - use the first one with a
        # tkhd we can read; good enough since we only care about the video track's rotation and
        # non-video traks essentially never carry a meaningful rotation matrix.
        while f.tell() < moov_end:
            header = _read_box_header(f)
            if header is None:
                break
            box_type, size, header_size = header
            payload_size = (size - header_size) if size else (moov_end - f.tell())
            trak_end = f.tell() + payload_size

            if box_type == 'trak':
                tkhd_size = _find_child_box(f, 'tkhd', trak_end)
                if tkhd_size is not None:
                    tkhd_payload = bytes(f.readBytes(tkhd_size))
                    if tkhd_payload:
                        version = tkhd_payload[0]
                        matrix_offset = _TKHD_VERSION1_HEADER if version == 1 else _TKHD_VERSION0_HEADER
                        if len(tkhd_payload) >= matrix_offset + _MATRIX_SIZE:
                            matrix = tkhd_payload[matrix_offset:matrix_offset + _MATRIX_SIZE]
                            return _rotation_from_matrix(matrix)

            f.seek(trak_end, 0)

        return None

    except Exception as e:
        Logger.warning(f"get_rotation: could not read rotation for [{file_path}]: {e}")
        return None
    finally:
        f.close()


def _find_video_codec_in_strl(f, strl_end):
    """
    Within an AVI 'strl' LIST, find its 'strh' stream header chunk and return the stream's codec
    FourCC if it's the video stream (fccType 'vids').

    :return: the 4-character codec FourCC, or None if this isn't a video stream / not found
    """
    while f.tell() < strl_end:
        chunk_header = bytes(f.readBytes(8))
        if len(chunk_header) < 8:
            return None
        fourcc, size = struct.unpack('<4sI', chunk_header)
        chunk_start = f.tell()
        padded_size = size + (size % 2)

        if fourcc == b'strh':
            # strh payload: fccType (4 bytes), fccHandler/codec (4 bytes), then more fields we
            # don't need.
            strh_header = bytes(f.readBytes(min(size, 8)))
            if len(strh_header) >= 8 and strh_header[0:4] == b'vids':
                return strh_header[4:8].decode('ascii', errors='replace')

        f.seek(chunk_start + padded_size, 0)

    return None


def _find_video_codec_in_hdrl(f, hdrl_end):
    """
    Within an AVI 'hdrl' LIST, find the first 'strl' LIST describing the video stream and return
    its codec FourCC.
    """
    while f.tell() < hdrl_end:
        chunk_header = bytes(f.readBytes(8))
        if len(chunk_header) < 8:
            return None
        fourcc, size = struct.unpack('<4sI', chunk_header)
        chunk_start = f.tell()
        padded_size = size + (size % 2)

        if fourcc == b'LIST':
            list_type = bytes(f.readBytes(4))
            if list_type == b'strl':
                codec = _find_video_codec_in_strl(f, chunk_start + padded_size)
                if codec:
                    return codec

        f.seek(chunk_start + padded_size, 0)

    return None


def get_avi_video_codec(file_path):
    """
    Read the FourCC of an AVI file's video stream (e.g. "MJPG", "DIVX"), by walking its RIFF
    header chunk structure - without downloading the whole file. Only the small header chunks
    (inside 'hdrl') are read; the actual (often huge) media payload in 'movi' is never reached,
    since 'hdrl' always precedes it.

    :param file_path: full path/URL of the .avi file
    :return: the video stream's codec FourCC, or None if it couldn't be determined
    """
    f = xbmcvfs.File(file_path)
    try:
        file_size = f.size()
        if file_size <= 12:
            return None

        header = bytes(f.readBytes(12))
        if header[0:4] != b'RIFF' or header[8:12] != b'AVI ':
            return None

        while f.tell() < file_size:
            chunk_header = bytes(f.readBytes(8))
            if len(chunk_header) < 8:
                return None
            fourcc, size = struct.unpack('<4sI', chunk_header)
            chunk_start = f.tell()
            padded_size = size + (size % 2)

            if fourcc == b'LIST':
                list_type = bytes(f.readBytes(4))
                if list_type == b'hdrl':
                    return _find_video_codec_in_hdrl(f, chunk_start + padded_size)
                if list_type == b'movi':
                    # hdrl always precedes movi in a valid AVI - if we've reached movi without
                    # having found/returned from hdrl above, there's nothing more to find.
                    return None

            f.seek(chunk_start + padded_size, 0)

        return None

    except Exception as e:
        Logger.warning(f"get_avi_video_codec: could not read codec for [{file_path}]: {e}")
        return None
    finally:
        f.close()


def probe_needs_software_decode(file_path):
    """
    Work out whether a file needs software decoding forced, based on whatever we can determine
    about its actual contents - a rotation matrix amcodec mishandles (MP4/MOV), or a video codec
    amcodec can't decode at all (AVI). Dispatches by file extension, since the two container
    formats need entirely different parsing.

    :param file_path: full path/URL of the video file
    :return: True/False if this could be confidently determined, or None if this file type isn't
        covered by either probe, or reading/parsing it failed
    """
    lower = file_path.lower()
    if lower.endswith(('.mp4', '.m4v', '.mov', '.3gp')):
        rotation = get_rotation(file_path)
        return None if rotation is None else rotation in BROKEN_ROTATIONS
    if lower.endswith('.avi'):
        codec = get_avi_video_codec(file_path)
        return None if codec is None else codec.upper() in BROKEN_AVI_CODECS
    return None
