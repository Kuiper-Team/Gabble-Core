from fastapi import APIRouter

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.channels as channels
import utilities.generation as generation

router = APIRouter()

@router.post("/channels")
async def r_channels(parameters: data_models.Channel):
    if not controls.access_to_channel(parameters.username, parameters.uuid, parameters.private_key): return presets.nopermission

    try:
        data = controls.fetch_from_db(channels, "uuid", parameters.uuid)
        if data is None: return presets.nochannel
    except Exception as code:
        return presets.auto(code)

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
async def channels_create(parameters: data_models.ChannelCreate):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_channel(parameters.username, parameters.uuid, parameters.private_key): return presets.nopermission

    try:
        channels.create(parameters.title, parameters.room_uuid, parameters.voice_channel, parameters.public_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/channels/delete")
async def channels_update(parameters: data_models.ChannelDelete):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_channel(parameters.channel_model.username, parameters.channel_model.uuid, parameters.channel_model.private_key): return presets.nopermission

    try:
        channels.delete(parameters.channel_model.uuid, parameters.room_uuid, parameters.public_key, parameters.channel_model.private_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/channels/messages") #Will be done later.
async def channels_messages(parameters: None):
    pass

@router.post("/channels/update")
async def channels_update(parameters: data_models.ChannelUpdate):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_channel(parameters.hash_credentials.username, parameters.channel_model.uuid, parameters.channel_model.private_key): return presets.nopermission

    if (
        parameters.settings is None and
        parameters.permission_map is None
    ): return presets.invalidformat

    try:
        if parameters.settings: settings = generation.rsa_decrypt(parameters.settings, parameters.channel_model.private_key)
        if parameters.permissions: permissions = generation.rsa_decrypt(parameters.permissions, parameters.channel_model.private_key)
        channels.update(parameters.channel_model.uuid, settings=settings, permissions=permissions)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success