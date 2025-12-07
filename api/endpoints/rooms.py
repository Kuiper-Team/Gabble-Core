from fastapi import APIRouter, Depends

import api.controls as controls
import api.data_models as data_models
import api.permissions as permissions
import api.presets as presets
import database.rooms as rooms
import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography

router = APIRouter()

@router.post("/rooms")
async def r_rooms(parameters: data_models.Room, token: str = Depends(controls.oauth2_scheme)):
    try:
        data = sql.select(rooms.table, "rooms", parameters.uuid, exception="noroom")[0]
    except Exception as code:
        return presets.auto(code)

    result = {
        "success": True,
        "data": {
            "public": {
                "uuid": parameters.uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channel_list(parameters.uuid, parameters.private_key),
                "members": rooms.members(parameters.uuid, parameters.private_key)
            }
        }
    }
    if parameters.user_id and parameters.private_key:
        if permissions.check(rooms.available_permissions(parameters.user_id, parameters.uuid, parameters.private_key), permissions.mask["write/permissions"]):
            result["data"]["private"]["permissions"] = cryptography.rsa_decrypt(data[6], parameters.private_key)
        if permissions.check(rooms.available_permissions(parameters.user_id, parameters.uuid, parameters.private_key), permissions.mask["write/room"]):
            result["data"]["private"]["settings"] = cryptography.rsa_decrypt(data[5], parameters.private_key)

    return result

@router.post("/rooms/create")
async def rooms_create(parameters: data_models.TitleRoom, token: str = Depends(controls.oauth2_scheme)):
    if not parameters.title.isascii: return presets.invalidformat

    try:
        public_key, private_key, uuid = rooms.create(parameters.title, parameters.hash_credentials.username)
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

@router.post("/rooms/delete")
async def rooms_delete(parameters: data_models.UUIDRoom, token: str = Depends(controls.oauth2_scheme)):
    if not permissions.check(rooms.available_permissions(parameters.user_id, parameters.uuid, parameters.private_key), permissions.mask["write/delete_room"]): return presets.nopermission

    try:
        rooms.delete(parameters.uuid, parameters.private_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/rooms/update") #Needs data validation
async def rooms_update(parameters: data_models.RoomUpdate, token: str = Depends(controls.oauth2_scheme)):
    if not permissions.check(rooms.available_permissions(parameters.uuid_room.user_id, parameters.uuid_room.uuid, parameters.uuid_room.private_key), permissions.mask["write/room"]): return presets.nopermission
    if parameters.settings is None and parameters.permissions is None: return presets.invalidformat

    try:
        if parameters.settings: settings = cryptography.rsa_decrypt(parameters.settings, parameters.uuid_room.private_key)
        if parameters.permissions: permissions_column = cryptography.rsa_decrypt(parameters.permissions, parameters.uuid_room.private_key)
        rooms.update(parameters.uuid_room.hash_credentials.username, settings=settings, permissions=permissions_column)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/rooms/members")
async def rooms_members(parameters: data_models.Member, token: str = Depends(controls.oauth2_scheme)):
    if not permissions.check(rooms.available_permissions(parameters.uuid_room.user_id, parameters.uuid_room.uuid, parameters.uuid_room.private_key), permissions.mask["write/room"]): return presets.nopermission

    try:
        is_member = parameters.member in rooms.members(parameters.uuid_room.uuid, parameters.uuid_room.private_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return {
            "success": True,
            "ismember": parameters.member in rooms.members(parameters.uuid_room.uuid, parameters.uuid_room.private_key)
        }

@router.post("/rooms/members/kick")
async def rooms_members_kick(parameters: data_models.Member, token: str = Depends(controls.oauth2_scheme)):
    if not permissions.check(rooms.available_permissions(parameters.uuid_room.user_id, parameters.uuid_room.uuid, parameters.uuid_room.private_key), permissions.mask["moderation/kick"]): return presets.nopermission

    try:
        rooms.kick_member(parameters.member, parameters.uuid_room.uuid, parameters.uuid_room.private_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/rooms/members/ban")
async def rooms_members_ban(parameters: data_models.BanMember, token: str = Depends(controls.oauth2_scheme)):
    if not permissions.check(rooms.available_permissions(parameters.uuid_room.user_id, parameters.uuid_room.uuid, parameters.uuid_room.private_key), permissions.mask["moderation/ban"]): return presets.nopermission

    try:
        rooms.ban_member(parameters.member, parameters.uuid_room.uuid, parameters.uuid_room.private_key, parameters.expiry)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/rooms/members/unban")
async def rooms_members_unban(parameters: data_models.UnbanMember, token: str = Depends(controls.oauth2_scheme)):
    if not permissions.check(rooms.available_permissions(parameters.uuid_room.user_id, parameters.uuid_room.uuid, parameters.uuid_room.private_key), permissions.mask["moderation/ban"]): return presets.nopermission

    try:
        rooms.unban_member(parameters.member, parameters.uuid_room.uuid, parameters.uuid_room.private_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success