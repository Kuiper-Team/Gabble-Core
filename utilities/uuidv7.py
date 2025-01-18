#Kaynak: https://codereview.stackexchange.com/q/294707
import datetime
import random
import time
import uuid

def dt_to_unix_ms(timestamp: datetime.datetime | None) -> int:
    if timestamp is None:
        unix_ts = time.time()
    elif isinstance(timestamp, datetime.datetime):
        unix_ts = timestamp.timestamp()
    else:
        raise TypeError('timestamp must be a datetime or None')

    unix_ts_ms = int(unix_ts * 1e3)

    if unix_ts_ms < 0:
        raise ValueError('timestamp cannot be negative')

    return unix_ts_ms

def rand_basis(rand: random.Random | None) -> bytes:
    if rand is None:
        randbytes = random.randbytes
    elif isinstance(rand, random.Random):
        randbytes = rand.randbytes
    else:
        raise TypeError('rand must be Random or None')

    return randbytes(n=16)

def uuid_v7(
    timestamp: datetime.datetime | None = None,
    rand: random.Random | None = None,
) -> uuid.UUID:

    unix_ts_ms = dt_to_unix_ms(timestamp)
    result = rand_basis(rand)

    result_c = (result[4] << 8) | result[5]

    result_d = result[8]

    a = (unix_ts_ms >> 16) & 0xFFFFFFFF
    b = unix_ts_ms & 0xFFFF
    c = (result_c & ~0xF000) | 0x7000

    d = (result_d & 0x3F) | 0x80

    final_d = bytearray(8)
    final_d[0] = d

    final_d[1:7] = result[9:15]

    final_bytes = (
        a.to_bytes(4, byteorder='big') +
        b.to_bytes(2, byteorder='big') +
        c.to_bytes(2, byteorder='big') +
        final_d
    )

    return uuid.UUID(bytes=final_bytes)