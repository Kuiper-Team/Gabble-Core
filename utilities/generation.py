import pyargon2
from datetime import datetime
from uuid import UUID

def add_zeros(number, full_digit_c): #Pozitif tam sayılar içindir.
    number_str = str(number)
    digit_c = len(number_str)
    if digit_c == full_digit_c:
        return number_str
    else:
        return (full_digit_c - digit_c) * "0" + number_str

def unix_timestamp(date_time):
    return datetime.timestamp(date_time) * 1000

def hashed_password(password):
    length = len(password)
    slice_index = length // 2 if length % 2 else length // 2 + 1

    return pyargon2.hash(password[:slice_index], password[slice_index:])

def message_id(time: datetime, user_id: UUID):
    return add_zeros(time.hour, 2) + add_zeros(time.minute, 2) + add_zeros(time.day, 2) + add_zeros(time.month, 2) + add_zeros(time.year, 4) + user_id.hex

def channel_key(channel_id: UUID, user_id: UUID, login_key: UUID):
    return channel_id.hex + user_id.hex + login_key.hex