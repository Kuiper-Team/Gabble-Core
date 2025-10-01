#A .env file containing an environmental variable for JWT secret key, labelled SECRET, must be created in this directory.
import jwt
from base64 import b64decode
from fastapi import APIRouter, Depends

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import api.endpoints.oauth2 as oauth2
import database.sqlite_wrapper as sql
import database.users as users
import utilities.cryptography as cryptography

router = APIRouter()

@router.post("/users")
async def r_users(parameters: data_models.User, token: str = Depends(controls.oauth2_scheme)):
    if not users.exists(parameters.user_id): return presets.nouser

    access_token = await controls.authenticate(token)
    try:
        data = sql.select(users.table, "uuid", parameters.user_id, exception="nouser")
    except Exception as code:
        return presets.auto(code)

    if parameters.user_id == access_token[1]:
        return {
            "success": True,
            "data": {
                "public": {
                    "display_name": b64decode(data[1]).decode(),
                    "user_id": parameters.user_id,
                    "biography": data[3],
                    "request_hash": data[4]
                },
                "private": data[5] #The client receives it encrypted, then decrypts from the client-stored hash.
            },
        }
    else:
        return {
            "success": True,
            "data": {
                "public": {
                    "display_name": b64decode(data[1]).decode(),
                    "user_id": parameters.uuid,
                    "biography": data[3],
                    "request_hash": data[4]
                }
            },
        }

@router.post("/users/create")
async def users_create(parameters: data_models.BasicCredentials):
    try:
        salt = users.create(parameters.user_id, parameters.password)
    except Exception as code:
        return presets.auto(code)
    else:
        return {
                "success": True,
                "user": {
                    "salt_b64": salt
                }
            }

@router.post("/users/delete")
async def users_delete(parameters: data_models.UserDelete, token: str = Depends(controls.oauth2_scheme)):
    if not users.exists(parameters.username): return presets.nouser

    try:
        users.delete(parameters.user_id, bytes.fromhex(parameters.hash_hex))
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/users/update") #https://www.slingacademy.com/article/json-parsing-in-pydantic/
async def users_update(parameters: data_models.UserUpdate, token: str = Depends(controls.oauth2_scheme)):
    if (
        parameters.display_name is None and
        parameters.biography is None and
        parameters.preferences is None and
        parameters.preferences_channels is None and
        parameters.preferences_conversations is None and
        parameters.preferences_rooms is None
    ): return presets.invalidformat

    def get_column(column):
        jwt.decode(token, oauth2.secret, algorithms=oauth2.algorithms)

        return sql.select(users.table, "user_id", parameters.user_id, column=column, exception="nouser")

    hash = bytes.fromhex(parameters.hash_hex)
    try:
        if parameters.display_name: display_name = get_column("display_name")
        if parameters.biography: biography = get_column("biography")
        if parameters.preferences: preferences = cryptography.aes_decrypt(get_column("preferences"), hash)
        if parameters.preferences_channels: preferences_channels = cryptography.aes_decrypt(get_column("preferences_channels"), hash)
        if parameters.preferences_conversations: preferences_conversations = cryptography.aes_decrypt(get_column("preferences_conversations"), hash)
        if parameters.preferences_rooms: preferences_rooms = cryptography.aes_decrypt(get_column("preferences_rooms"), hash)

        users.update(parameters.user_id,
            display_name=display_name,
            biography=biography,
            preferences=preferences,
            preferences_channels=preferences_channels,
            preferences_conversations=preferences_conversations,
            preferences_rooms=preferences_rooms
        )
    except Exception as code:
        return presets.auto(code)

    return presets.success