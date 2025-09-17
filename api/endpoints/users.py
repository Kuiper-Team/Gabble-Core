#A .env file containing an environmental variable for JWT secret key, labelled SECRET, must be created in this directory.
from fastapi import APIRouter, Depends

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.sqlite_wrapper as sql
import database.users as users
import utilities.cryptography as cryptography

router = APIRouter()

@router.post("/users")
async def r_users(parameters: data_models.User, token: str = Depends(controls.oauth2_scheme)):
    if not users.exists(parameters.uuid): return presets.nouser
    access_token = await controls.authenticate(token)
    request_uuid = access_token[1]
    try:
        data = sql.select(users.table, "uuid", parameters.uuid, exception="nouser")
    except Exception as code:
        return presets.auto(code)

    if parameters.uuid == request_uuid:
        return {
            "success": True,
            "data": {
                "public": {
                    "username": data[0],
                    "uuid": parameters.uuid,
                    "biography": data[3],
                    "request_hash": data[4]
                },
                "private": data[5] #The client receives it encrypted, then decrypts from the stored hash.
            },
        }
    else:
        return {
            "success": True,
            "data": {
                "public": {
                    "username": data[0],
                    "uuid": parameters.uuid,
                    "biography": data[3],
                    "request_hash": data[4]
                }
            },
        }

@router.post("/users/create")
async def users_create(parameters: data_models.BasicCredentials):
    try:
        uuid, salt = users.create(parameters.username, parameters.password)
    except Exception as code:
        return presets.auto(code)
    else:
        return {
                "success": True,
                "user": {
                    "uuid": uuid,
                    "salt_b64": salt
                }
            }

@router.post("/users/delete") #WILL BE UPDATED
async def users_delete(parameters: data_models.User):
    if not users.exists(parameters.username): return presets.nouser

    try:
        users.delete(parameters.username, parameters.hash)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/users/update") #WILL BE UPDATED
async def users_update(parameters: data_models.UserUpdate):
    if not controls.verify_hash(parameters.username, parameters.hash): return presets.incorrecthash

    if (
        parameters.channel_settings is None and
        parameters.settings is None and
        parameters.room_settings is None
    ): return presets.invalidformat

    try:
        if parameters.channel_settings: channel_settings = cryptography.aes_decrypt(parameters.channel_settings, parameters.hash)
        if parameters.settings: settings = cryptography.aes_decrypt(parameters.settings, parameters.hash)
        if parameters.room_settings: room_settings = cryptography.aes_decrypt(parameters.room_settings, parameters.hash)
        users.update(parameters.username, display_name=parameters.display_name, settings=settings, room_settings=room_settings, channel_settings=channel_settings, biography=parameters.biography)
    except Exception as code:
        return presets.auto(code)

    return presets.success