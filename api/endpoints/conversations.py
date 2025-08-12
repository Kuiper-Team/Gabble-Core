from fastapi import APIRouter

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.conversations as conversations
import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography

router = APIRouter()

@router.post("/conversations")
async def r_conversations(parameters: data_models.Conversation):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_conversation(parameters.hash_credentials.username, parameters.uuid, parameters.private_key): return presets.nopermission

    try:
        users = cryptography.aes_decrypt(sql.select(conversations.table, "uuid", parameters.uuid, column="users")[0], parameters.private_key).split(",")
        users = [item for item in users if item != ""]

        public_key = sql.select(conversations.table, "uuid", parameters.uuid, column="public_key")[0]
    except Exception:
        return presets.noconversation
    else:
        return {
            "success": True,
            "data": {
                "uuid": parameters.uuid,
                "users": users,
                "public_key": public_key
            }
        }

@router.post("/conversations/create")
async def conversations_create(parameters: data_models.ConversationCreate):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash

    try:
        uuid, public_key, private_key = conversations.create(parameters.username1, parameters.username2)
    except Exception as code:
        return presets.auto(code)
    else:
        return {
            "success": True,
            "room": {
                "uuid": uuid,
                "public_key": public_key,
                "private_key": private_key
            }
        }

@router.post("/conversations/delete")
async def conversations_delete(parameters: data_models.Conversation):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_conversation(parameters.hash_credentials.username, parameters.uuid, parameters.private_key): return presets.nopermission

    try:
        conversations.delete(parameters.uuid)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/conversations/messages") #Will be done later.
async def conversations_messages(parameters: data_models.Conversation):
    pass