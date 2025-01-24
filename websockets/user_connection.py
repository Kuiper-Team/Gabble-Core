#BURASI TAMAMLANACAK.

import asyncio
import os
import websockets
from sys import path

path.append("..")

import utilities.log as log
import utilities.validation as validation
from utilities.check_ports import check_port
from config import user_connection

script_name = os.path.basename(__file__)

async def stream(ws):
    while True:
        received = await ws.recv()

        if received == "Q":
            break
        elif validation.message_id(received):
            #!!! Kimlik doğrulamasından geçilmeden channelde mesaj gönderilemeyecek. (session_uuids)
            #!!! İlk atılan mesaj geçerli bir giriş anahtarıysa devam edecek, değilse WebSocket sunucusu bağlantıyı koparacak.
            #!!! Mesaj formatı: uuid (boşluksuz) (32 bayt) + room_uuid (boşluksuz) (32 bayt) + channel_uuid (boşluksuz) (32 bayt) + message
            #await ws.send(received[97:])
        else:
            await ws.send("invalidmessage")

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