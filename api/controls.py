import jwt
from base64 import b64decode
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from functools import wraps
from uuid import UUID

import api.endpoints.oauth2 as oauth2
import database.sqlite_wrapper as sql
import database.users as users
import utilities.cryptography as cryptography

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth2")

def verify_password(uuid, password):
    salt = b64decode(sql.select("users", "uuid", uuid, column="salt_b64", exception="nouser")[0])
    hash = cryptography.argon2_hash(password, custom_salt=salt)[0].hex()
    try:
        return UUID(hex=users.private(uuid, hash)["discriminator"]).version == 7
    except Exception:
        return False

async def authenticate(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, oauth2.secret, algorithms=["HS256"]).get("sub")
    except Exception:
        return False
    else:
        return True

#Decorator factory
def oauth2_post(router: APIRouter, path: str, **kwargs):
    def decorator(function):
        @router.post(path, **kwargs)
        @wraps(function)
        async def wrapper(authentication = Depends(authenticate), **kwargs):
            return await function(authentication, **kwargs)
        return wrapper
    return decorator

#def permission(): -> Bitwise permissions model…
#def verify_private_key(uuid, private_key): -> JSON checking model…