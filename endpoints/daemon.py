from error.output import output, CodeType
from ws_implementation.handler import start_client
from websockets import *
from utils.config import target_ip, port
from utils.mirror_logging import *
import camera.camera_utils as cutils
from utils.log import log, ts
from asyncio import gather
# from endpoints._depr_wsutils import *
from endpoints.advaws import *
import json

CHUNK_SIZE = 9000

closer = lambda: None

async def DaemonTasks(websocket:ClientConnection):
    global closer
    closer = websocket.close

    await Sender.handshake(report_as=EndpointMode.DAEMON)
    await ContinuouslyVideoClip(websocket)


async def ContinuouslyVideoClip(ws:ClientConnection):
    # Avoid import errors
    import camera.picamera_interface as cami

    log("Starting continuous video clipping...")
    while True:
        save_folder, output = await cami.clip_video()

        with open(save_folder + '/' + output, 'rb') as f:
            buffer = [
                DataInstrument(data=json.dumps({
                    'filename': output
                }), ptag=ProtoTags.META).tobin()
            ]
            while frame := f.read1(CHUNK_SIZE):
                buffer.append(frame)
        # TODO this is some incompetent buffer system

        await Sender.send_large_buffer(buffer, tag=ProtoTags.RECV_FILE)



        # TODO reimplement
        # await send_flag_out(ws, StateFlags.RECV_FILE)
        # await ws_send_dict(ws, {
        #     'filename': output
        # })
        # await send_filestream_from_fs(ws, save_path + '/' + output)


        # await websocket_sender(f"FILENAME: {output}\n".encode('utf-8'))
        # packets = cutils.get_video_binary(save_path=save_path, video_output=output)
        # for packet in packets:
        #     await websocket_sender(packet)
        # # await websocket_sender(cutils.get_video_binary(save_path=save_path, video_output=output))




async def DaemonMain():
    log(f"Websockets connection attempt to {target_ip}:{port} as daemon...")

    async def hooks(websocket):
        # print('Hooked!')
        Sender.hook(ws=websocket)
        await WSQueue.hook(ws=websocket)
        # await gather(WSQueue.hook(ws=websocket), Sender.hook(ws=websocket))

    async def daemon_scheduler(ws):
        # if WSQueue.abort_not_hooked() or Sender.abort_not_hooked():
        #     print('Unhooked!', WSQueue.ws, Sender.ws)
        # else: await DaemonTasks(ws)
        if not WSQueue.abort_not_hooked() and not Sender.abort_not_hooked():
            await DaemonTasks(ws)
    
    async def dual(ws:ClientConnection): await gather(hooks(ws), daemon_scheduler(ws))

    await start_client(
        target_ip=target_ip,
        port=port,
        action=dual
    )

