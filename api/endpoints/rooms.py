from fastapi import APIRouter

import api.controls as controls
import api.data_models as data_models
import api.permissions as permissions
import api.presets as presets
import database.rooms as rooms
import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography

router = APIRouter()

@router.post("/rooms")
async def r_rooms(parameters: data_models.Room):
    #permissions.check()

    access = rooms.has_permissions(parameters.uuid, parameters.hash_credentials.username, ("access_to_settings", "access_to_permissions"), parameters.private_key)
    try:
        data = sql.select(rooms.table, "rooms", parameters.uuid, exception="noroom")[0]
    except Exception as code:
        return presets.auto(code)

    if access[0] and access[1]:
        return {
            "success": True,
            "data": {
                "uuid": parameters.uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channel_list(parameters.uuid, parameters.private_key),
                "members": rooms.members(parameters.uuid, parameters.private_key),
                "sensitive": {
                    "settings": cryptography.rsa_decrypt(data[5], parameters.private_key),
                    "permissions": cryptography.rsa_decrypt(data[6], parameters.private_key)
                }
            }
        }
    elif access[0]:
        return {
            "success": True,
            "data": {
                "uuid": parameters.uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channel_list(parameters.uuid, parameters.private_key),
                "members": rooms.members(parameters.uuid, parameters.private_key),
                "sensitive": {
                    "settings": cryptography.rsa_decrypt(data[5], parameters.private_key)
                }
            }
        }
    elif access[1]:
        return {
            "success": True,
            "data": {
                "uuid": parameters.uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channel_list(parameters.uuid, parameters.private_key),
                "members": rooms.members(parameters.uuid, parameters.private_key),
                "sensitive": {
                    "permissions": cryptography.rsa_decrypt(data[6], parameters.private_key)
                }
            }
        }
    else:
        return {
            "success": True,
            "data": {
                "uuid": parameters.uuid,
                "title": data[0],
                "public_key": data[2],
                "channels": rooms.channel_list(parameters.uuid, parameters.private_key),
                "members": rooms.members(parameters.uuid, parameters.private_key)
            }
        }

@router.post("/rooms/create")
async def rooms_create(parameters: data_models.TitleRoom):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
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
async def rooms_delete(parameters: data_models.UUIDRoom):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_room(parameters.hash_credentials.username, parameters.uuid, parameters.private_key) or not rooms.has_permissions(parameters.hash_credentials.username, parameters.uuid, ("delete_room",), parameters.private_key): return presets.nopermission

    try:
        rooms.delete(parameters.uuid, parameters.private_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/rooms/update") #Needs data validation
async def rooms_update(parameters: data_models.RoomUpdate):
    if not controls.verify_hash(parameters.uuid_room.hash_credentials.username, parameters.uuid_room.hash_credentials.username): return presets.incorrecthash
    if not rooms.has_permissions(parameters.uuid_room.hash_credentials.username, parameters.uuid_room.uuid, ("update_settings",), parameters.uuid_room.private_key): return presets.nopermission

    if (
        parameters.settings is None and
        parameters.permissions is None
    ): return presets.invalidformat

    try:
        if parameters.settings: settings = cryptography.rsa_decrypt(parameters.settings, parameters.uuid_room.private_key)
        if parameters.permissions: permissions = cryptography.rsa_decrypt(parameters.permissions, parameters.uuid_room.private_key)
        rooms.update(parameters.uuid_room.hash_credentials.username, settings=settings, permissions=permissions)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/rooms/members")
async def rooms_members(parameters: data_models.Member):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_room(parameters.hash_credentials.username, parameters.uuid_room.uuid, parameters.uuid_room.private_key): return presets.nopermission

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
async def rooms_members_kick(parameters: data_models.Member):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_room(parameters.hash_credentials.username, parameters.uuid_room.uuid, parameters.uuid_room.private_key) or not rooms.has_permissions(parameters.uuid_room.uuid, parameters.hash_credentials.username, ("kick_members",), parameters.uuid_room.private_key): return presets.nopermission

    try:
        rooms.kick_member(parameters.member, parameters.uuid_room.uuid, parameters.uuid_room.private_key)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success

@router.post("/rooms/members/ban")
async def rooms_members_ban(parameters: data_models.BanMember):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.access_to_room(parameters.hash_credentials.username, parameters.uuid_room.uuid, parameters.uuid_room.private_key) or not rooms.has_permissions(parameters.uuid_room.uuid, parameters.hash_credentials.username, ("ban_members",), parameters.uuid_room.private_key): return presets.nopermission

    try:
        rooms.ban_member(parameters.member, parameters.uuid_room.uuid, parameters.uuid_room.private_key, expiry_day=parameters.expiry_day, expiry_month=parameters.expiry_month, expiry_year=parameters.expiry_year)
    except Exception as code:
        return presets.auto(code)
    else:
        return presets.success