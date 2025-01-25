import pyargon2
import random
from Crypto.Cipher import AES
from datetime import datetime
from string import ascii_letters, digits, punctuation
from uuid import UUID

#Kullanılan şifreleme metotları:
#1. Argon2 (hash) -> Bir veriyi kullanıcı HASH'İ İLE güvenli bir şekilde şifreleyip saklamak istediğimizde...
#2. SHA256 (hash) + AES -> Bir veriyi hızlı deşifre edilebilmek üzere kullanıcı HASH'İ İLE şifreleyip saklamak istediğimizde...

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

def aes_encrypt(text, hash):
    cipher = AES.new(key=hash[:16], mode=AES.MODE_CFB, iv=hash[16:].encode("utf-8"))

    return cipher.encrypt(text.encode("utf-8"))

def aes_decrypt(encrypted, hash):
    cipher = AES.new(key=hash[:16], mode=AES.MODE_CFB, iv=hash[16:].encode("utf-8"))

    return cipher.decrypt(encrypted).decode("utf-8")

def ws_message(time: datetime, user_id: UUID):
    return add_zeros(time.hour, 2) + add_zeros(time.minute, 2) + add_zeros(time.day, 2) + add_zeros(time.month, 2) + add_zeros(time.year, 4) + user_id.hex

def channel_key(channel_id: UUID, user_id: UUID, login_key: UUID):
    return channel_id.hex + user_id.hex + login_key.hex

scl = ascii_letters + digits + punctuation
def password(length, character_list=scl):
    password = ""
    for character in range(length):
        password += random.choice(character_list)

    return password