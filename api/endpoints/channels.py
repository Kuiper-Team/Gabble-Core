from fastapi import APIRouter, responses

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.channels as channels
import utilities.generation as generation

router = APIRouter(prefix="/channels")

@router.post("/channels") #Permissions are needed to see settings and so on.
async def channels(parameters: data_models.Channel):
    if not controls.access_to_channel(parameters.username, parameters.uuid, parameters.private_key): return presets.nopermission

    try:
        data = controls.fetch_from_db(channels, "uuid", parameters.uuid)
        if data is None: return presets.nochannel
    except Exception as code:
        return responses.JSONResponse(
            status_code=presets.response_code[code],
            content={
                "success": False,
                "error": code
            }
        )

    return {
        "success": True,
        "data": {
            "title": data[0],
            "uuid": parameters.uuid,
            "room_uuid": data[2],
            "type": data[3],
            "tags": data[6]
        }
    }

@router.post("/channels/create")
async def channels_create(parameters: None):
    pass

@router.post("/channels/messages")
async def channels_messages(parameters: None):
    pass

@router.post("/channels/create")
async def channels_update(parameters: None):
    pass