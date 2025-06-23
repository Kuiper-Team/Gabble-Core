import json
from fastapi import APIRouter, responses

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.users as users
import utilities.generation as generation

router = APIRouter(
    prefix="/users"
)

@router.post("/users")
async def users(parameters: data_models.HashCredentials):
    if not controls.user_exists(parameters.username): return presets.nouser
    access = controls.verify_hash(parameters.username, parameters.hash)

    try:
        data = controls.fetch_from_db("users", "username", parameters.username)
    except Exception as code:
        return responses.JSONResponse(
            status_code=presets.response_code[code],
            content={
                "success": False,
                "error": code
            }
        )

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
                    "settings": generation.aes_decrypt(data[2], parameters.hash),
                    "room_settings": generation.aes_decrypt(data[3], parameters.hash),
                    "channel_settings": generation.aes_decrypt(data[4], parameters.hash),
                    "key_chain": json.dumps(generation.aes_decrypt(data[9], parameters.hash))
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
    if controls.user_exists(parameters.username): return presets.userexists

    try:
        hash, salt = users.create(parameters.username, parameters.password)
    except Exception as code:
        return responses.JSONResponse(
            status_code=presets.response_code[code],
            content={
                "success": False,
                "error": code
            }
        )
    else:
        return {
                "success": True,
                "user": {
                    "username": parameters.username,
                    "hash": hash,
                    "salt": salt
                }
            }

@router.post("/users/delete")
async def users_delete(parameters: data_models.HashCredentials):
    if not controls.user_exists(parameters.username): return presets.nouser
    if not controls.verify_hash(parameters.username, parameters.hash): return presets.incorrecthash

    try:
        users.delete(parameters.username, parameters.hash)
    except Exception as code:
        return responses.JSONResponse(
            status_code=presets.response_code[code],
            content={
                "success": False,
                "error": code
            }
        )
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
        if parameters.channel_settings: channel_settings = generation.aes_decrypt(parameters.channel_settings, parameters.hash)
        if parameters.settings: settings = generation.aes_decrypt(parameters.settings, parameters.hash)
        if parameters.room_settings: room_settings = generation.aes_decrypt(parameters.room_settings, parameters.hash)
        users.update(parameters.username, display_name=parameters.display_name, settings=settings, room_settings=room_settings, channel_settings=channel_settings, biography=parameters.biography)
    except Exception as code:
        return {
                "success": False,
                "error": code
            }

    return presets.success