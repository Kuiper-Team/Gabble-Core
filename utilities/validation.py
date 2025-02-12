from datetime import datetime
from uuid import UUID

import utilities.generation as generation

def uuid(uuid_str, version):
    try:
        object = UUID(uuid_str)
    except ValueError:
        return False
    else:
        return object.version == version

def message_id(message):
    try:
        length = len(message)
        if (
            96 < length <= message.character_limit + 96 and
            uuid(message[:33], 7) and
            uuid(message[33:65], 7)
        ):
            return True
        else:
            return False
    except ValueError:
        return False

def timestamp(timestamp):
    return timestamp > generation.unix_timestamp(datetime.now())

def integer(value):
    try:
        value == int(value)
    except ValueError:
        return False
    else:
        return True