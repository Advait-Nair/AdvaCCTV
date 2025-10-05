from error.output import output, CodeType
from ws_implementation.handler import start_client
from websockets import *
from utils.config import target_ip, port
import camera.camera_utils as cutils
from utils.log import log, ts
from asyncio import gather
# from endpoints._depr_wsutils import *
from endpoints.advaws import *

closer = lambda: None

async def DaemonTasks(websocket:ClientConnection):
    global closer
    closer = websocket.close

    
    print('dtasks triggered')
    print('websockets hooked')

    await Sender.handshake(report_as=EndpointMode.DAEMON)
    # print('hs sent')

    ack_empty = WSQueue()
    ack_empty.add_filters([ProtoTags.ACK, ProtoTags.EMPTY])
    ack_empty.trigger(lambda din: log('ACK/EMPTY', din.tostr()))
    # print('ack_empty',ack_empty)

    jdict = WSQueue()

    jdict.add_filters([ProtoTags.JDICT])
    jdict.trigger(lambda din: log(din.todict()))
    # print('jdict',jdict)

    await Sender.send_msg('HEY SERVER')
    # print('msg->',jdict)
    await Sender.send_dict({
        'testdict1': 1
    })
    # print('dict->',jdict)

    await Sender.send('ACKnowledgement', ProtoTags.ACK)
    await Sender.send('Custom Message', ProtoTags.MSG)
    await Sender.send('Empty', ProtoTags.EMPTY)
    await Sender.send('META to filterout', ProtoTags.META)

        

    # await ContinuouslyVideoClip(websocket)

async def ContinuouslyVideoClip(ws:ClientConnection):
    # Avoid import errors
    import camera.picamera_interface as cami

    log("Starting continuous video clipping...")
    while True:
        save_path, output = await cami.clip_video()


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
    log("Starting WS Daemon...")

    async def hooks(websocket):
        print('Hooked!')
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

