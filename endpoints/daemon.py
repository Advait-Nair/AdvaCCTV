from error.output import output, CodeType
from ws_implementation.handler import start_client
from websockets import *
from utils.config import target_ip, port
import camera.camera_utils as cutils
from utils.log import log, ts



async def DaemonTasks(websocket:ClientConnection):
    await websocket.send("AdvaCCTV Daemon - WS Handshake at" + ts())
    message = await websocket.recv()
    log('From Server: ', message)

    await ContinuouslyVideoClip(websocket.send_data)

async def ContinuouslyVideoClip(websocket_sender):
    import camera.picamera_interface as cami
    while True:
        save_path, output = cami.clip_video()
        await websocket_sender(cutils.get_video_binary(save_path=save_path, output=output))



async def DaemonMain():
    await start_client(
        target_ip=target_ip,
        port=port,
        action=DaemonTasks
    )
