from error.output import output, CodeType
from ws_implementation.handler import start_client
from websockets import *
from env_data import target_ip, port


async def DaemonTasks(websocket:ClientConnection):
    await websocket.send("Intuition culminates complexity.")
    message = await websocket.recv()
    print(message)

def DaemonMain():
    start_client(
        target_ip=target_ip,
        port=port,
        action=DaemonTasks
    )