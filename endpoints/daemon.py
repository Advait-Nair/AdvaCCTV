from error.output import output, CodeType
from ws_implementation.handler import start_client
from websockets import *
from utils.config import target_ip, port
import camera.camera_utils as cutils
from utils.log import log, ts
from endpoints.wsutils import *


sent_handshake = False
async def DaemonTasks(websocket:ClientConnection):
    global sent_handshake
    if not sent_handshake:
        await send_daemon_handshake(ws=websocket)

    await ContinuouslyVideoClip(websocket)

async def ContinuouslyVideoClip(ws:ClientConnection):
    # Avoid import errors
    import camera.picamera_interface as cami

    log("Starting continuous video clipping...")
    while True:
        save_path, output = await cami.clip_video()

        await send_flag_out(ws, StateFlags.RECV_FILE)
        await ws_send_dict(ws, {
            'filename': output
        })
        await send_filestream_from_fs(ws, save_path)


        # await websocket_sender(f"FILENAME: {output}\n".encode('utf-8'))
        # packets = cutils.get_video_binary(save_path=save_path, video_output=output)
        # for packet in packets:
        #     await websocket_sender(packet)
        # # await websocket_sender(cutils.get_video_binary(save_path=save_path, video_output=output))




async def DaemonMain():
    log("Starting WS Daemon...")
    await start_client(
        target_ip=target_ip,
        port=port,
        action=DaemonTasks
    )
