from base64 import b64decode, b64encode
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
from secrets import choice

def add_zeros(number, full_digit_c): #Pozitif tam sayılar içindir.
    number_str = str(number)
    digit_c = len(number_str)
    if digit_c == full_digit_c:
        return number_str
    else:
        return (full_digit_c - digit_c) * "0" + number_str

def unix_timestamp(date_time):
    return datetime.timestamp(date_time) * 1000

def aes_encrypt(text, key):
    data = text.encode()

    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext_b = cipher.encrypt(pad(data, AES.block_size))

    return b64encode(cipher.iv).decode() + b64encode(ciphertext_b).decode()

def aes_decrypt(ciphertext, key):
    decoded = b64decode(ciphertext)
    encrypted = decoded[16:]

    cipher = AES.new(key, AES.MODE_CBC, decoded[:16])

    return unpad(cipher.decrypt(encrypted), AES.block_size)

def rsa_generate_pair(bits=1024):
    pair = RSA.generate(bits, Random.new().read)
    public_key = pair.publickey().exportKey("PEM")
    private_key = pair.export_key("PEM")

    return public_key, private_key

def rsa_encrypt(text, public_key):
    encoded = text.encode()
    rsa_public_key = PKCS1_OAEP.new(RSA.importKey(public_key))
    ciphertext = rsa_public_key.encrypt(encoded)

    return b64encode(ciphertext)

def rsa_decrypt(ciphertext, private_key):
    rsa_private_key = PKCS1_OAEP.new(RSA.importKey(b64decode(private_key)))
    decrypted_text = rsa_private_key.decrypt(ciphertext)

    return decrypted_text

def random_string(length, characters="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"):
    result = ""
    for column in range(length):
        result += choice(characters)

    return result