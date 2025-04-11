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

def timestamp(timestamp):
    return timestamp > generation.unix_timestamp(datetime.now())

def integer(value):
    try:
        int(value)
    except ValueError:
        return False
    else:
        return True