from bossanova808.utilities import send_kodi_json

# Shared between the context menu scripts and the settings action (which run as their own
# short-lived processes) and the service (which does the actual work) - they ask the service via a
# Kodi notification, and for a play request the service confirms via a Home window property.
NOTIFY_SENDER = "script.limp"
NOTIFY_MESSAGE = "SoftwareDecode"
NOTIFY_SERIES_CHANGED = "SeriesListChanged"
ACK_PROPERTY = "Limp.SoftwareDecodeAck"

# The TV shows set to always use software decoding, in the addon's profile folder
SERIES_FILE = "series.json"

# Set on the Home window by the service while the "show context menu item" setting is on - the
# context items' <visible> conditions in addon.xml check this (they can't read addon settings
# themselves), so keep the two in step.
CONTEXT_MENU_PROPERTY = "Limp.ContextMenu"

# Set on the Home window while the focused item's TV show is on the series list, so the context
# menu can offer "stop" rather than "start" for it (addon.xml checks this too).
SERIES_LISTED_PROPERTY = "Limp.SeriesListed"

# Set on the Home window by the service when running on Amlogic, so the settings can show the
# Amlogic-only option (settings.xml checks this)
AMLOGIC_PROPERTY = "Limp.Amlogic"


def notify_service(message, data=None):
    """
    Send a message to the running Limp service.

    :param message: one of the NOTIFY_ message names above
    :param data: optional JSON-able data to send along with it
    """
    send_kodi_json(f'Tell the Limp service: {message}', {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "JSONRPC.NotifyAll",
            "params": {"sender": NOTIFY_SENDER, "message": message, "data": data if data is not None else {}},
    })
