import json

import database.rooms as rooms
import database.sqlite_wrapper as sql
import utilities.generation as generation
from utilities.uuidv7 import uuid_v7

table = "channels"

sql.table(table,
    (
        sql.C("title", sql.Types.TEXT, not_null=True),
        sql.C("uuid", sql.Types.TEXT, not_null=True),
        sql.C("room_uuid", sql.Types.TEXT, not_null=True),
        sql.C("type", sql.Types.INTEGER, not_null=True),
        sql.C("settings", sql.Types.TEXT, not_null=True),
        sql.C("permissions", sql.Types.TEXT, not_null=True)
    ),
    primary_key="uuid"
)

default_settings = {
    #
}

default_permissions = {
    #
}

def create(title, room_uuid, voice_channel, public_key):
    #Type 0: Text channel
    #Type 1: Voice channel
    sql.insert(table,
       (
           generation.rsa_encrypt(title, public_key),
           uuid_v7().hex,
           room_uuid,
           generation.rsa_encrypt("1" if voice_channel else "0", public_key),
           generation.rsa_encrypt(default_settings, public_key),
           generation.rsa_encrypt(default_permissions, public_key)
       ),
       exception="channelexists"
    )

def delete(uuid, room_uuid, public_key, private_key):
    sql.delete(table, "uuid", uuid, exception="nochannel")

    channels = rooms.channels(uuid, private_key)
    sql.update(table, "channels", generation.rsa_encrypt(json.dumps(channels.pop(uuid)), public_key), "uuid", uuid, exception="noroom")

def update(uuid, settings=None, permissions=None):
    sql.update(table, "settings", settings, "uuid", uuid, condition=settings, exception="nouser")
    sql.update(table, "permissions", permissions, "uuid", uuid, condition=permissions, exception="nouser")

def room_of(uuid):
    return sql.select(table, "uuid", uuid, column="room_uuid", exception="nochannel")