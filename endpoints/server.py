from error.output import output, CodeType
from ws_implementation.handler import start_websocket_server
from websockets import *
from utils.config import target_ip, port



async def ServerTasks(websocket:ServerConnection):
    async for message in websocket:
        print('Bro legit said', message)
        await websocket.send("calm")



async def ServerMain():
    await start_websocket_server(
        target_ip=target_ip,
        port=port,
        action=ServerTasks
    )