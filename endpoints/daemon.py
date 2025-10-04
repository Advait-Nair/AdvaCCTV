from error.output import output, CodeType
from ws_implementation.handler import start_client
from websockets import *
from utils.config import target_ip, port
import camera.camera_utils as cutils
from utils.log import log, ts
# from endpoints._depr_wsutils import *
from endpoints.advaws import *


async def DaemonTasks(websocket:ClientConnection):
    print('dtasks triggered')
    await WSQueue.hook(ws=websocket)
    await Sender.hook(ws=websocket)
    print('websockets hooked')

    await Sender.handshake(report_as=EndpointMode.DAEMON)
    print('hs sent')

    ack_empty = WSQueue()
    ack_empty.add_filters([ProtoTags.ACK, ProtoTags.EMPTY])
    ack_empty.trigger(lambda din: log('ACK/EMPTY', din.tostr()))
    print('ack_empty',ack_empty)

    jdict = WSQueue()

    jdict.add_filters([ProtoTags.JDICT])
    jdict.trigger(lambda din: log(din.todict()))
    print('jdict',jdict)

    Sender.send_msg('HEY SERVER')
    print('msg->',jdict)
    Sender.send_dict({
        'testdict1': 1
    })
    print('dict->',jdict)

    Sender.send('ACKnowledgement', ProtoTags.ACK)
    Sender.send('Custom Message', ProtoTags.MSG)
    Sender.send('Empty', ProtoTags.EMPTY)
    Sender.send('META to filterout', ProtoTags.META)
    print('sender.send ack msg empty meta->',jdict)

        

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
    await start_client(
        target_ip=target_ip,
        port=port,
        action=DaemonTasks
    )
