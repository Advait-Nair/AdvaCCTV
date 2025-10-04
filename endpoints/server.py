from error.output import output, CodeType
from ws_implementation.handler import start_websocket_server
from websockets import *
from utils.log import error, log, ts
from utils.config import properties_cfg
from asyncio import gather
from utils.config import port
# from endpoints._depr_wsutils import *
from endpoints.advaws import *


VIDEO_SAVE_PATH = properties_cfg.get('video_save_path') or './videos'




# TODO once this basic system works,
# TODO a continuous livestream will be sent over websockets as "live". If the socket fails,
# TODO that video buffer is locally saved to videos folder, and once the socket is restored,
# TODO all unsent videos are sent over the socket in sequence and are flagged as "old footage".

closer = lambda: None

async def ServerTasks(websocket:ServerConnection):
    global closer
    closer = websocket.close

    await Sender.handshake(report_as=EndpointMode.SERVER)

    ack_empty = WSQueue()
    ack_empty.add_filters([ProtoTags.EMPTY, ProtoTags.ACK])
    ack_empty.trigger(lambda din: log('ACK/EMPTY', din.tostr()))

    await Sender.send_msg('HEY SERVER')
    await Sender.send_dict({
        'testdict_server': 1
    })

    await Sender.send('S ACKnowledgement', ProtoTags.ACK)
    await Sender.send('S Custom Message', ProtoTags.MSG)
    await Sender.send('S Empty', ProtoTags.EMPTY)
    await Sender.send('S META to filterout', ProtoTags.META)

        # TODO reimplement
        # flag = await get_flag_in(websocket)

        # if flag == StateFlags.RECV_FILE:
        #     file_metadata = await ws_get_dict(websocket)
        #     log(file_metadata)
        #     await recv_filestream(websocket,writes_to=file_metadata.get('filename'))



        # async for message in websocket:

            # if isinstance(message, str):
            #     log('From Daemon:', message)
            #     await websocket.send("Adva CCTV Server - WS Handshake returned at " + ts())
            # elif isinstance(message, bytes):

            #     log(f"Received {len(message)} bytes of video data.")

                # The video is sent over as binary
                # Extract the filename from the binary data
                # try:
                #     header, video_data = message.split(b'\n', 1)
                #     filename = header.decode('utf-8').replace("FILENAME:","").strip()
                #     # Save the video data to a file
                #     with open(f"{VIDEO_SAVE_PATH}/{filename}", "wb") as f:
                #         f.write(video_data)
                #     log(f"Saved video to {VIDEO_SAVE_PATH}/{filename}")
                # except Exception as e:
                #     error("Error processing received video data. The server will continue operating.\n\nError details:\n", e)
                #     continue


async def ServerMain():
    target_ip = get_ip()
    log(f"Starting WS Server: {target_ip}:{port}...")

    async def hooks(websocket):
        print('Hooked!')
        Sender.hook(ws=websocket)
        await WSQueue.hook(ws=websocket)

    async def server_scheduler(ws):
        # if WSQueue.abort_not_hooked() or Sender.abort_not_hooked():
        #     print('Unhooked!', WSQueue.ws, Sender.ws)
        # else: await ServerTasks(ws)
        if not WSQueue.abort_not_hooked() and not Sender.abort_not_hooked():
            await ServerTasks(ws)

    async def hooks(websocket):
        Sender.hook(ws=websocket)
        await WSQueue.hook(ws=websocket)
    
    async def dual(ws:ClientConnection): await gather(hooks(ws), server_scheduler(ws))

    await start_websocket_server(
        target_ip=target_ip,
        port=port,
        action=dual
    )