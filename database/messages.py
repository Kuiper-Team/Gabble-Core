from datetime import datetime

import database.channels as channels
import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography
import utilities.generation as generation
from utilities.uuidv7 import uuid_v7

table = "messages"

sql.table(table,
    (
        sql.C("body", sql.Types.TEXT, not_null=True),
        sql.C("uuid", sql.Types.TEXT, not_null=True),
        sql.C("username", sql.Types.TEXT, not_null=True),
        sql.C("room_uuid", sql.Types.TEXT),
        sql.C("channel_uuid", sql.Types.TEXT, not_null=True),
        sql.C("timestamp", sql.Types.INTEGER, not_null=True)
    ),
    primary_key="uuid"
)

def create(body, username, channel_uuid, public_key):
    uuid = uuid_v7().hex
    timestamp = generation.unix_timestamp(datetime.now())

    sql.insert(table,
        (
            cryptography.rsa_encrypt(body, public_key),
            uuid,
            username,
            channels.room_of(channel_uuid),
            channel_uuid,
            cryptography.rsa_encrypt(timestamp, public_key)
        ),
        exception="couldntinsert"
    )

    return uuid, timestamp

def delete(uuid):
    sql.delete(table, "uuid", uuid, exception="nomessage")

def edit(new_body, uuid, channel_uuid, public_key):
    sql.update(table, "body", cryptography.aes_encrypt(new_body, public_key), "uuid", uuid, exception="nomessage")

def exists(uuid):
    data = sql.select(table, "uuid", uuid, safe=True)

    return data is not None