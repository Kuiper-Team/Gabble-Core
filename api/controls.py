import jwt
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from functools import wraps
from uuid import UUID

import database.users as users
import api.endpoints.oauth2 as oauth2

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth2")

def verify_hash(uuid, hash): #Should be fixed
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