#FastAPI has its own WebSocket decorators.
import asyncio
import os
import websockets
from sys import path

path.append("..")

import utilities.log as log
from utilities.check_port import check_port

script_name = os.path.basename(__file__)
host = "0.0.0.0"
port = 80

async def stream(ws):
    session_uuid = await ws.recv()
    #There are going to be some controls and nested commands alongside "await ws.send()" lines.

async def serve():
    async with websockets.serve(stream, host, port):
        await asyncio.Future()

if check_port(host, port):
    try:
        log.success("The server {} is up on ws://{}:{}.".format(script_name, host, port))
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
    except BaseException as error:
        log.failure(str(error))
        exit(1)
else:
    log.failure("The port {} is busy for the websocket server {}.".format(port, script_name))
    exit(1)