# Shared between the context menu script (which runs as its own short-lived process) and the
# service (which does the actual work) - the script asks the service via a Kodi notification, and
# the service confirms via a Home window property.
NOTIFY_SENDER = "script.limp"
NOTIFY_MESSAGE = "SoftwareDecode"
ACK_PROPERTY = "Limp.SoftwareDecodeAck"

# Set on the Home window by the service while the "show context menu item" setting is on - the
# context item's <visible> condition in addon.xml checks this (it can't read addon settings itself),
# so keep the two in step.
CONTEXT_MENU_PROPERTY = "Limp.ContextMenu"
