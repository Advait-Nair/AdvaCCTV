from error.output import output, CodeType
from ws_implementation.handler import start_websocket_server
from websockets import *
from utils.config import target_ip, port
from utils.log import log, ts


async def ServerTasks(websocket:ServerConnection):
    log("Beginning Server Tasks...")
    async for message in websocket:
        log('From Daemon:', message)
        await websocket.send("Adva CCTV Server - WS Handshake returned at " + ts())



async def ServerMain():
    log(f"Starting WS Server: {target_ip}:{port}...")
    await start_websocket_server(
        target_ip=target_ip,
        port=port,
        action=ServerTasks
    )