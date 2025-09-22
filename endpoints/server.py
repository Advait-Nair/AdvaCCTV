from error.output import output, CodeType
from ws_implementation.handler import start_websocket_server
from websockets import *
from utils.config import target_ip, port
from utils.log import log, ts


async def ServerTasks(websocket:ServerConnection):
    async for message in websocket:
        log('From Daemon ', message)
        await websocket.send("Adva CCTV Server - WS Handshake at" + ts())



async def ServerMain():
    await start_websocket_server(
        target_ip=target_ip,
        port=port,
        action=ServerTasks
    )