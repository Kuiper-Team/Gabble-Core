from fastapi import WebSocket

from app import api

#Ideas:
#1. Check if a client is active by sending regular messages and let the client respond, and if it doesn't, change user's status as inactive.
#2. Basic commands to handle some user requests faster than HTTP requests.

#Just a starter code for WebSockets.
@api.websocket("/adapter")
async def adapter(connection: WebSocket):
    await connection.accept()
    while True:
        received = await connection.receive_text()

        await connection.send_text(received)