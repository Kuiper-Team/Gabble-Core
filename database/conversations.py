import utilities.generation as generation
import database.sqlite_wrapper as sql
from utilities.uuidv7 import uuid_v7

table = "conversations"

sql.table(table,
    (
        sql.C("uuid", sql.Types.TEXT, not_null=True),
        sql.C("users", sql.Types.TEXT, not_null=True),
        sql.C("public_key", sql.Types.TEXT, not_null=True)
    ),
    primary_key="uuid"
)

def create(username1, username2):
    key_pair = generation.rsa_generate_pair(),
    public_key = key_pair[0]
    uuid = uuid_v7().hex
    sql.insert(table, (uuid, generation.rsa_encrypt(username1 + "," + username2, public_key), public_key), exception="conversationexists")

    return uuid, public_key, key_pair[1]

def delete(uuid):
    sql.delete(table, "uuid", uuid, exception="noconversation")
    #Perhaps, key_chain cleanup?