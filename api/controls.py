import jwt
from base64 import b64decode
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from uuid import UUID

import api.endpoints.oauth2 as oauth2
import database.sqlite_wrapper as sql
import database.users as users
import utilities.cryptography as cryptography

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth2")

def verify_password(uuid, password):
    salt = b64decode(sql.select("users", "user_id", uuid, column="salt_b64", exception="nouser")[0])
    hash = cryptography.argon2_hash(password, custom_salt=salt)[0].hex()
    try:
        return UUID(hex=users.private(uuid, hash)["discriminator"]).version == 7
    except Exception:
        return False

async def authenticate(token: str = Depends(oauth2_scheme)) -> tuple[bool, str]:
    try:
        sub = jwt.decode(token, oauth2.secret, algorithms=oauth2.algorithms).get("sub")
    except Exception:
        return False, ""
    else:
        return True, sub


def verify_model(data, model: type[BaseModel]):
    try:
        model.model_validate(data)
    except Exception:
        return False
    else:
        return True

#def permission(): -> Bitwise permissions model…
#def verify_private_key(uuid, private_key): -> JSON checking model for rooms and conversations…