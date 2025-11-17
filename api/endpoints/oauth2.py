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
algorithms = ["HS256"]

router = APIRouter()

@router.post("/oauth2")
async def r_oauth2(parameters: data_models.OAuth2):
    if not users.exists(parameters.user_id): return presets.nouser
    if not controls.verify_password(parameters.user_id, parameters.password): return presets.incorrectpassword

    return {
        "access_token": cryptography.jwt_access_token(
            {"sub": parameters.user_id},
            timedelta(minutes=parameters.expiry_minutes),
            secret
        ),
        "token_type": "bearer"
    }