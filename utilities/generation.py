import pyargon2
from base64 import b64decode, b64encode
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from datetime import datetime

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
    iv = Random.get_random_bytes(16)
    cipher = AES.new(key=bytes.fromhex(hash), mode=AES.MODE_CBC, iv=iv)

    return iv.decode("utf-8") + cipher.encrypt(text.encode("utf-8")).decode("utf-8")

def aes_decrypt(ciphertext, hash):
    iv = ciphertext[:16].encode("utf-8")
    cipher = AES.new(key=bytes.fromhex(hash), mode=AES.MODE_CBC, iv=iv)

    return cipher.decrypt(ciphertext).decode("utf-8")

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

def random_sha256_hash():
    return SHA256.new(Random.get_random_bytes(64)).hexdigest()