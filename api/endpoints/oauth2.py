#A .env file containing an environmental variable for the path to the database, labelled OAUTH2_SECRET, must be created in this directory.
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import APIRouter
from os import getenv

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.users as users
import utilities.cryptography as cryptography

load_dotenv()
secret = getenv("OAUTH2_SECRET")

router = APIRouter()

#Additional JWT data "hash" to supply a lot of endpoints with an AES key?

@router.post("/oauth2")
async def r_oauth2(parameters: data_models.OAuth2):
    if not users.exists(parameters.uuid): return presets.nouser
    if not controls.verify_password(parameters.uuid, parameters.password): return presets.incorrectpassword

    return {
        "access_token": cryptography.jwt_access_token(
            {"sub": parameters.uuid},
            timedelta(minutes=parameters.expiry_minutes),
            secret
        ),
        "token_type": "bearer"
    }