from datetime import datetime
from uuid import UUID

import utilities.generation as generation

def uuid_v4(uuid_str):
    object = None
    try:
        object = UUID(uuid_str)
    except ValueError:
        return False

    return object.version == 4

def uuid_v7(uuid_str):
    object = None
    try:
        object = UUID(uuid_str)
    except ValueError:
        return False

    return object.version == 7

def message_id(message):
    try:
        length = len(message)
        if (
            96 < length <= message.character_limit + 96 and
            uuid_v7(message[:33]) and
            uuid_v7(message[33:65])
        ):
            return True
        else:
            return False
    except ValueError:
        return False

def timestamp(timestamp):
    return timestamp > generation.unix_timestamp(datetime.now())

def uuid_timestamp_to_unix(uuid):
    pass #Hazır değil.