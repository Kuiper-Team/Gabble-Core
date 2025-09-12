import jwt
import pyargon2
import secrets
from base64 import b64decode, b64encode
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from datetime import datetime, timedelta, timezone


#Argon2 Functions
def argon2_hash(password: str, custom_salt=None) -> tuple[bytes, bytes]:
    salt = secrets.token_bytes(32) if custom_salt is None else custom_salt
    hash = pyargon2.hash_bytes(password.encode(), salt, hash_len=16, encoding="raw")

    return hash, salt

#AES Functions
def aes_encrypt(text, hash: bytes or str):
    data = text.encode()

    if isinstance(hash, str):
        hash_b = bytes.fromhex(hash)
    else:
        hash_b = hash

    cipher = AES.new(hash_b, AES.MODE_CBC)
    ciphertext_b = cipher.encrypt(pad(data, AES.block_size))

    return b64encode(cipher.iv + ciphertext_b).decode()

def aes_decrypt(ciphertext, hash):
    hash_b = bytes.fromhex(hash)

    decoded = b64decode(ciphertext)
    encrypted = decoded[16:]

    cipher = AES.new(hash_b, AES.MODE_CBC, iv=decoded[:16])

    return unpad(cipher.decrypt(encrypted), AES.block_size)

#RSA Functions
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

#JWT Functions
def jwt_access_token(data: dict, expiry_delta: timedelta, secret: str, algorithm="HS256"):
    expiry = datetime.now(timezone.utc) + expiry_delta

    to_encode = data.copy()
    to_encode.update({"exp": expiry})

    return jwt.encode(to_encode, secret, algorithm=algorithm)