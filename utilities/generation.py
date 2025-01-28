import pyargon2
import random
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from datetime import datetime
from string import ascii_letters, digits, punctuation

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

#encode(): str -> byte
#decode(): byte -> str
def aes_encrypt(text, hash):
    iv = get_random_bytes(16)
    cipher = AES.new(key=bytes.fromhex(hash), mode=AES.MODE_CBC, iv=iv)

    return iv.decode("utf-8") + cipher.encrypt(text.encode("utf-8")).decode("utf-8")

def aes_decrypt(ciphertext, hash):
    iv = ciphertext[:16].encode("utf-8")
    cipher = AES.new(key=bytes.fromhex(hash), mode=AES.MODE_CBC, iv=iv)

    return cipher.decrypt(ciphertext).decode("utf-8")

scl = ascii_letters + digits + punctuation
def password(length, character_list=scl):
    password = ""
    for character in range(length):
        password += random.choice(character_list)

    return password