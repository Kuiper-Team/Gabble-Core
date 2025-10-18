from hashlib import sha256
import json
from uuid import uuid4

import database.rooms as rooms
import database.sqlite_wrapper as sql
import database.users as users
import utilities.cryptography as cryptography

table = "invites"

sql.table(table,
    (
        sql.C("uuid", sql.Types.TEXT, not_null=True),
        sql.C("action", sql.Types.TEXT, not_null=True),
        sql.C("expiry", sql.Types.INTEGER, not_null=True)
    ),
    primary_key="uuid"
)

def create(action_type: int, action_whitelist: tuple[str], action_blacklist: tuple[str], key: tuple[str], expiry, passcode):
    sql.insert(table, (
            uuid4().hex,
            cryptography.aes_encrypt(
                {
                    "type": action_type,
                    "whitelist": action_whitelist,
                    "blacklist": action_blacklist,
                    "parameters": []
                },
                sha256(passcode.encode()).digest()
            ),
            expiry,
        ),
        exception="couldntinsert"
    )

def exists(uuid):
    try:
        sql.select(table, "uuid", uuid)
    except Exception:
        return False
    else:
        return True

def verify_passcode(uuid, passcode):
    try:
        cryptography.aes_decrypt(sql.select(table, "uuid", uuid, column="action", exception="noinvite")[0], sha256(passcode.encode()).digest())
    except Exception:
        return False
    else:
        return True

#Types:
#0: Connection requests
#1: Room invites
def accept(user_id, uuid, passcode):
    action = get_action(uuid, passcode)
    type = action[0]
    parameters = action[3]

    if type == 0: #parameters: [user_1, user_2]
        if not user_id == parameters[1] or user_id == parameters[0]: raise Exception("notinvitee")
        users.add_connection(parameters[0], parameters[1])
    elif type == 1: #parameters: [uuid, private_key]
        rooms.add_member(user_id, parameters[0], parameters[1])
    else:
        raise Exception("invalidformat")

def get_action(uuid, passcode):
    action = json.cryptography.aes_decrypt(sql.select(table, "uuid", uuid, column="action", exception="noinvite")[0], sha256(passcode.encode()).digest())

    return {
        "type": action[0],
        "whitelist": action[1],
        "blacklist": action[2],
        "parameters": action[3]
    }