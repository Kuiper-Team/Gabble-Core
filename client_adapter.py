import asyncio
import os
import websockets
from sys import path

path.append("..")

import utilities.log as log

script_name = os.path.basename(__file__)

async def stream(ws):
    session_uuid = await ws.recv()
    #There are going to be some controls and nested commands alongside "await ws.send()" lines.

async def serve():
    async with websockets.serve(stream, "0.0.0.0", 80):
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