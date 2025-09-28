from error.output import output, CodeType
from ws_implementation.handler import start_client
from websockets import *
from utils.config import target_ip, port
import camera.camera_utils as cutils
from utils.log import log, ts



async def DaemonTasks(websocket:ClientConnection):
    await websocket.send("AdvaCCTV Daemon - WS Handshake sent at " + ts())
    message = await websocket.recv()
    log('From Server:', message)

    await ContinuouslyVideoClip(websocket.send_data)

async def ContinuouslyVideoClip(websocket_sender):
    import camera.picamera_interface as cami
    log("Starting continuous video clipping...")
    while True:
        save_path, output = await cami.clip_video()
        await websocket_sender(cutils.get_video_binary(save_path=save_path, video_output=output))
        # TODO once this basic system works,
        # TODO a continuous livestream will be sent over websockets as "live". If the socket fails,
        # TODO that video buffer is locally saved to videos folder, and once the socket is restored,
        # TODO all unsent videos are sent over the socket in sequence and are flagged as "old footage".



async def DaemonMain():
    log("Starting WS Daemon...")
    await start_client(
        target_ip=target_ip,
        port=port,
        action=DaemonTasks
    )
