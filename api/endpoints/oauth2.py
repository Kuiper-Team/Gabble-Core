#A .env file containing an environmental variable for the path to the database, labelled OAUTH2_SECRET, must be created in this directory.
from base64 import b64decode
from datetime import timedelta
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from os import getenv

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.sqlite_wrapper as sql
import database.users as users
import utilities.cryptography as cryptography

load_dotenv()

secret = getenv("OAUTH2_SECRET")
oauth2 = OAuth2PasswordBearer(tokenUrl="/oauth2")

router = APIRouter()

@router.post("/oauth2")
async def r_oauth2(parameters: data_models.OAuth2):
    if not users.exists(parameters.username): return presets.nouser
    #if not controls.verify_hash(parameters.username, parameters.hash): return presets.incorrectpassword
    #verify_hash() -> authenticate() -> Will be like get_current_user() from the tutorial

    return {
        "access_token": cryptography.jwt_access_token({"sub": parameters.username}, timedelta(minutes=parameters.expiry_minutes), secret),
        "token_type": "bearer"
    }