#Şifreleme yapılacak.

import asyncio
import websockets
from sys import path

path.append("..")

import utilities.log as log
import utilities.validation as validation
from utilities.check_ports import check_port
from config import text_channel

async def stream(ws):
    while True:
        received = await ws.recv()
        #Mesajı HAFTANIN GÜNÜ İLE BERABER veritabanına işle.

        if received == "Q":
            break
        elif validation.message_id(received):
            #Kimlik doğrulamasından geçilmeden channelde mesaj gönderilemeyecek. (timed_keys)
            #İlk atılan mesaj geçerli bir giriş anahtarıysa devam edecek, değilse WebSocket sunucusu bağlantıyı koparacak.
            #Giriş anahtarı formatı: {kanal ID, kullanıcı adı, (belirlenen zaman damgasına kadar geçerli olacak) anahtar}
            await ws.send(received[44:])
        else:
            await ws.send("HATA: Mesajınızın formatı geçersizdir.")

async def serve():
    async with websockets.serve(stream, text_channel.host, text_channel.port):
        await asyncio.Future()

if check_port(text_channel.host, text_channel.port):
    try:
        log.success("Kanal sunucusu, ws://{}:{} adresinde çalışıyor.".format(text_channel.host, text_channel.port))
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
    except BaseException as error:
        log.failure(str(error))
        exit(1)
else:
    log.failure("Kanal WebSocket sunucusunun portu {} müsait değil.".format(text_channel.port))
    exit(1)