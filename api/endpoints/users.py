#A .env file containing an environmental variable for JWT secret key, labelled SECRET, must be created in this directory.
import json
from fastapi import APIRouter

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.sqlite_wrapper as sql
import database.users as users
import utilities.cryptography as cryptography

router = APIRouter()

@router.post("/users")
async def r_users(parameters: data_models.HashCredentials):
    if not users.exists(parameters.username): return presets.nouser
    access = controls.verify_hash(parameters.username, parameters.hash)

    try:
        data = sql.select(users.table, "username", parameters.username, exception="nouser")[0]
    except Exception as code:
        return presets.auto(code)

    if access:
        return {
            "success": True,
            "data": {
                "public": {
                    "username": parameters.username,
                    "display_name": data[1],
                    "biography": data[6],
                    "request_hash": data[7]
                },
                "private": {
                    "settings": cryptography.aes_decrypt(data[2], parameters.hash),
                    "room_settings": cryptography.aes_decrypt(data[3], parameters.hash),
                    "channel_settings": cryptography.aes_decrypt(data[4], parameters.hash),
                    "key_chain": json.dumps(cryptography.aes_decrypt(data[9], parameters.hash))
                }
            },
        }
    else:
        return {
            "success": True,
            "data": {
                "public": {
                    "username": parameters.username,
                    "display_name": data[1],
                    "biography": data[6],
                    "request_hash": data[7]
                }
            },
        }

@router.post("/users/create")
async def users_create(parameters: data_models.BasicCredentials):
    if users.exists(parameters.username): return presets.userexists

    try:
        key = users.create(parameters.username, parameters.password)
    except Exception as code:
        return presets.auto(code)
    else:
        return {
                "success": True,
                "user": {
                    "username": parameters.username,
                    "key": key
                }
            }

@router.post("/users/delete")
async def users_delete(parameters: data_models.HashCredentials):
    if not users.exists(parameters.username): return presets.nouser
    if not controls.verify_hash(parameters.username, parameters.hash): return presets.incorrecthash

    try:
        users.delete(parameters.username, parameters.hash)
    except Exception as code:
        print(code)
        return presets.auto(code)
    else:
        return presets.success

@router.post("/users/update")
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