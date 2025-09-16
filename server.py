from error.output import output, CodeType
from ws_implementation.handler import start_websocket_server
from websockets import *
from env_data import target_ip, port



async def ServerTasks(websocket:ServerConnection):
    async for message in websocket:
        await websocket.send(message)



def ServerMain():
    start_websocket_server(
        target_ip=target_ip,
        port=port,
        action=ServerTasks
    )