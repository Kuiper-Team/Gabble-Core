import json
import sqlite3
from datetime import datetime

import database.sqlite_wrapper as sql
import utilities.cryptography as cryptography
import utilities.generation as generation
from utilities.uuidv7 import uuid_v7

table = "rooms"

sql.table(table,
    (
        sql.C("title", sql.Types.TEXT, not_null=True),
        sql.C("uuid", sql.Types.TEXT, not_null=True),
        sql.C("public_key", sql.Types.TEXT, not_null=True),
        sql.C("channels", sql.Types.TEXT),
        sql.C("members", sql.Types.TEXT, not_null=True),
        sql.C("settings", sql.Types.TEXT, not_null=True),
        sql.C("permissions", sql.Types.TEXT, not_null=True),
        sql.C("blacklist", sql.Types.TEXT, not_null=True),
    ),
    primary_key="uuid"
)

default_settings = json.dumps(
    {
        "icon": 0
    }
)

default_permissions = json.dumps(
    {
        "tags": {},
        "members": {}
    }
)

default_blacklist = json.dumps(
    {}
)

def create(title, username):
    key_pair = cryptography.rsa_generate_pair()
    public_key = key_pair[0]
    uuid = uuid_v7().hex
    sql.insert(table,
        (
            cryptography.rsa_encrypt(title, public_key),
            uuid,
            public_key,
            None,
            cryptography.rsa_encrypt(username, public_key),
            cryptography.rsa_encrypt(default_settings, public_key),
            cryptography.rsa_encrypt(default_permissions, public_key),
            cryptography.rsa_encrypt(default_blacklist, public_key)
        ),
        exception="roomexists"
    )

    return public_key, key_pair[1], uuid

def delete(uuid):
    sql.delete(table, "uuid", uuid, exception="noroom")

def update(uuid, settings=None, permissions=None):
    sql.update(table, "settings", settings, "uuid", uuid, settings, exception="noroom")
    sql.update(table, "permissions", permissions, "uuid", uuid, permissions, exception="noroom")

def has_permissions(uuid, username, requested, private_key):
    permissions = json.loads(
        cryptography.rsa_decrypt(
            sql.select(table, "uuid", uuid, column="permissions", safe=True)[0],
            private_key
        )
    )

    result = []
    for permission in requested:
        result.append(permissions["members"][username][permission])

    return result

def channels(uuid, private_key):
    channels = cryptography.rsa_decrypt(
        sql.select(table, "uuid", uuid, column="members", exception="noroom")[0],
        private_key
    )

    return channels.split(",") if channels is not None else []

def public_key(uuid):
    key = sql.select(table, "uuid", uuid, column="public_key", exception="noroom")[0]

    return key

def members(uuid, private_key):
    members = cryptography.rsa_decrypt(
        sql.select(table, "uuid", uuid, column="members", exception="noroom")[0],
        private_key
    )

    return members.split(",")

def add_member(new_member, uuid, private_key):
    members_list = members(uuid, private_key)
    if new_member in members_list:
        raise Exception("alreadyamember")

    sql.update(table,
        "members",
        cryptography.rsa_encrypt(json.dumps(json.loads(members_list.update({new_member: generation.unix_timestamp(datetime.now())}))), public_key(uuid)),
        "uuid",
        uuid,
        exception="noroom"
    )

def kick_member(member, uuid, private_key):
    members_list = members(uuid, private_key)
    if not member in members:
        raise Exception("nomember")

    sql.update(table,
        "members",
        cryptography.rsa_encrypt(json.dumps(json.loads(members_list.pop(member))), public_key(uuid)),
        "uuid",
        uuid,
        exception="noroom"
    )

def ban_member(member, uuid, private_key, expiry_day=None, expiry_month=None, expiry_year=None):
    if not member in members(uuid, private_key):
        raise Exception("nomember")

    object = json.loads(
        cryptography.rsa_decrypt(
            sql.select(table, "uuid", uuid, column="blacklist", exception="noroom")[0],
            private_key
        )
    )
    new_data = json.dumps(
        object.update({member: f"{expiry_day}-{expiry_month}-{expiry_year}" if expiry_day and expiry_month and expiry_year else 0})
    )

    sql.update(table, "blacklist", new_data, "username", member, exception="noroom")

def unban_member(): #To be done
    pass

def exists(uuid):
    data = sql.select(table, "uuid", uuid, safe=True)

    return data is not None