#I can use Kafka instead of the database based inbox system.
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, responses
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from os import getenv
from pydantic import ValidationError
from typing import Annotated

import api.data_models as data_models
import api.presets as presets
import database.sqlite_wrapper as sql
import database.users as users
from api.endpoints import home, channels, conversations, invites, messages, rooms, users

api = FastAPI(
    title="Gabble",
    version="1.0.0"
)

load_dotenv()
secret = getenv("SECRET")

oauth2 = OAuth2PasswordBearer(tokenUrl="login")
algorithm = "HS256"

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta:
        expiry = datetime.now(timezone.utc) + expires_delta
    else:
        expiry = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode = data.copy()
    to_encode.update({"expiry": expiry})

    return jwt.encode(to_encode, secret, algorithm=algorithm)

async def check_jwt(user: data_models.HashCredentials, token: Annotated[str, Depends(oauth2)]):
    exception = HTTPException(
        status_code=401,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        username = jwt.decode(token, secret, algorithms=[algorithm]).get("sub")
        if username is None:
            raise exception

        token_data = data_models.Username(username=username)
    except jwt.exceptions.InvalidTokenError:
        raise exception

    return True

@api.post("/login")
async def users_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if not users.exists(form_data.username): return {"error": "nouser"} #TEMPORARY

    user = sql.select("users", "username", form_data.username, column="username")[0]
    if not user:
        raise HTTPException(
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expiry = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expiry
    )

    return {
        "access_token": access_token,
        "type": "bearer"
    }

@api.exception_handler(500)
async def error_500(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "internalservererror"
        }
    )

@api.exception_handler(400)
async def error_400(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "badrequest"
        }
    )

@api.exception_handler(401)
async def error_401(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=401,
        content={
            "success": False,
            "error": "unauthorized"
        }
    )

@api.exception_handler(403)
async def error_403(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=403,
        content={
            "success": False,
            "error": "forbidden"
        }
    )

@api.exception_handler(404)
async def error_404(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "notfound"
        }
    )

@api.exception_handler(405)
async def error_405(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=405,
        content={
            "success": False,
            "error": "methodnotallowed"
        }
    )

@api.exception_handler(415)
async def error_415(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=415,
        content={
            "success": False,
            "error": "unsupportedmediatype"
        }
    )

@api.exception_handler(ValidationError)
async def validation_error(request: Request, exception: ValidationError):
    return responses.JSONResponse(
        status_code=422,
        content=presets.invalidformat
    )

api.include_router(home.router)
api.include_router(channels.router)
api.include_router(conversations.router)
api.include_router(invites.router)
api.include_router(messages.router)
api.include_router(rooms.router)
api.include_router(users.router)
