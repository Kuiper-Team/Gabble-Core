import pyargon2

import database.rooms as rooms
import database.sqlite_wrapper as sql
import database.users as users
import utilities.cryptography as cryptography
from uuid import uuid4

table = "invites"

sql.table(table,
    (
        sql.C("uuid", sql.Types.TEXT, not_null=True),
        sql.C("inviter", sql.Types.TEXT, not_null=True),
        sql.C("expiry", sql.Types.INTEGER, not_null=True),
        sql.C("result", sql.Types.TEXT, not_null=True),
    ),
    primary_key="uuid"
)

def create(inviter, expiry, result, passcode):
    request_hash = sql.select("users", "username", inviter, column="request_hash", exception="nouser")[0]
    hash = cryptography.argon2_hash(request_hash, custom_salt=passcode)

    sql.insert(table, (
            uuid4().hex,
            inviter,
            cryptography.aes_encrypt(expiry, hash)
        ),
        exception="couldntinsert"
    )

    return hash

def withdraw(uuid):
    sql.delete(table, "uuid", uuid, exception="norequest")

#Options for "type":
#f: Friend request
#r: Room invite
def accept(uuid, passcode, room_private_key=None):
    inviter = sql.select(table, "uuid", uuid, column="inviter", exception="noinvite")[0]
    result = get_result(uuid, inviter, passcode)

    if result[0] == "f": #f,username1,username2
        users.add_friends(result[1], result[2])
    elif result[0] == "r" and room_private_key: #r,uuid,username
        rooms.add_member(result[2], result[1], room_private_key)
    else:
        raise Exception("invalidformat")

    withdraw(uuid)

def get_result(uuid, inviter, passcode):
    return cryptography.aes_decrypt(
        sql.select(table, "uuid", uuid, column="result")[0],
        pyargon2.hash(sql.select("users", "username", inviter, column="request_hash")[0], passcode)
    ).split(",")