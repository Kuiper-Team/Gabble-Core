from fastapi import APIRouter

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.channels as channels
import database.messages as messages
import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography

router = APIRouter()

@router.post("/messages")
async def r_messages(parameters: data_models.UUIDRoom):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not messages.exists(parameters.uuid): return presets.nomessage
    if not controls.access_to_channel(parameters.hash_credentials.username, parameters.uuid, parameters.private_key): return presets.nopermission

    try:
        data = sql.select(messages.table, "uuid", parameters.uuid, exception="nomessage")[0]
    except Exception as code:
        return presets.auto(code)

    return {
        "success": True,
        "data": {
            "uuid": parameters.uuid,
            "room_uuid": data[2],
            "channel_uuid": data[3],
            "timestamp": cryptography.rsa_decrypt(data[4], parameters.private_key),
            "body": cryptography.rsa_decrypt(data[0], parameters.private_key)
        },
    }

@router.post("/messages/create")
async def messages_create(parameters: data_models.MessageCreate):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_channel(parameters.hash_credentials.username, parameters.channel_uuid, parameters.private_key): return presets.nopermission

    try:
        data = messages.create(parameters.body, parameters.hash_credentials.username, parameters.channel_uuid, parameters.public_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return {
            "success": True,
            "message": {
                "message": parameters.body,
                "uuid": data[0],
                "room_uuid": channels.room_of(parameters.channel_uuid),
                "channel_uuid": parameters.channel_uuid,
                "timestamp": data[1]
            }
        }

@router.post("/messages/delete")
async def messages_delete(parameters: data_models.MessageDelete):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not messages.exists(parameters.uuid): return presets.nomessage
    if not controls.access_to_channel(parameters.hash_credentials.username, parameters.channel_uuid, parameters.private_key): return presets.nopermission

    try:
        messages.delete(parameters.uuid)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/messages/edit")
async def messages_edit(parameters: data_models.MessageEdit):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not messages.exists(parameters.uuid): return presets.nomessage
    if not controls.access_to_channel(parameters.hash_credentials.username, parameters.channel_uuid, parameters.private_key): return presets.nopermission
    if (
            cryptography.rsa_decrypt(
                sql.select(messages.table, "uuid", parameters.uuid, column="body", exception="nomessage"),
                parameters.private_key
            ) == parameters.new_body
    ): return presets.sameasprevious

    try:
        messages.edit(parameters.new_body, parameters.uuid, parameters.channel_uuid, parameters.private_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success