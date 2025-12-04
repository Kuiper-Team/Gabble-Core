#GENERIC
version = "1.0"
endpoint_prefix = f"/{ version }"

#PERMISSIONS
permissions = (
    "read/channels",
    "read/past_messages",

    "write/channels",
    "write/invites",
    "write/messages",
    "write/room",
    "write/tags",

    "moderation/kick",
    "moderation/ban",

    "voice/join",
    "voice/speak",
    "voice/video"
)