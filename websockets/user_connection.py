import asyncio
import os
import sqlite3
import websockets
from sys import path

path.append("..")

import database.messages as messages
import utilities.log as log
import utilities.validation as validation
from utilities.check_ports import check_port
from utilities.uuidv7 import uuid_v7
from config import user_connection
from database.connection import cursor

script_name = os.path.basename(__file__)

async def stream(ws):
    session_uuid = await ws.recv()
    if validation.check_session_uuid(session_uuid):
        while True:
            received = await ws.recv()

            if received == "Q":
                break
            elif validation.message_id(received):
                hash = None
                try:
                    hash = cursor.execute("SELECT hash FROM session_uuids WHERE uuid = ?", (received[:33],)).fetchone()[0]
                except sqlite3.OperationalError:
                    await ws.send("incorrectsessionuuid")
                    break
                else:
                    #Mesaj formatı: session_uuid (boşluksuz) + room_uuid (boşluksuz) (32 bayt) + channel_uuid (boşluksuz) (32 bayt) + message
                    uuid = uuid_v7().hex
                    messages.create(received[96:], uuid, received[32:64], received[64:96], hash)

                    await ws.send(uuid)
            else:
                await ws.send("invalidmessage")
                break
    else:
        await ws.send("incorrectsessionuuid")

async def serve():
    async with websockets.serve(stream, user_connection.host, user_connection.port):
        await asyncio.Future()

if check_port(user_connection.host, user_connection.port):
    try:
        log.success("{} sunucusu, ws://{}:{} adresinde çalışıyor.".format(script_name, user_connection.host, user_connection.port))
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
    except BaseException as error:
        log.failure(str(error))
        exit(1)
else:
    log.failure("{} WebSocket sunucusunun portu {} müsait değil.".format(script_name, user_connection.port))
    exit(1)