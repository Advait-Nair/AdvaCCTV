from error.output import output, CodeType
from ws_implementation.handler import start_websocket_server
from websockets import *
from utils.config import target_ip, port
from utils.log import error, log, ts
from utils.config import properties_cfg

VIDEO_SAVE_PATH = properties_cfg.get('video_save_path') or './videos'

async def ServerTasks(websocket:ServerConnection):
    async for message in websocket:
        if isinstance(message, str):
            log('From Daemon:', message)
            await websocket.send("Adva CCTV Server - WS Handshake returned at " + ts())
        elif isinstance(message, bytes):
            log(f"Received {len(message)} bytes of video data.")
            # TODO once this basic system works,
            # TODO a continuous livestream will be sent over websockets as "live". If the socket fails,
            # TODO that video buffer is locally saved to videos folder, and once the socket is restored,
            # TODO all unsent videos are sent over the socket in sequence and are flagged as "old footage".

            # The video is sent over as binary
            # Extract the filename from the binary data
            try:
                header, video_data = message.split(b'\n', 1)
                filename = header.decode('utf-8').replace("FILENAME:","").strip()
                # Save the video data to a file
                with open(f"{VIDEO_SAVE_PATH}/{filename}", "wb") as f:
                    f.write(video_data)
                log(f"Saved video to {VIDEO_SAVE_PATH}/{filename}")
            except Exception as e:
                error("Error processing received video data. The server will continue operating.\n\nError details:\n", e)
                continue


async def ServerMain():
    log(f"Starting WS Server: {target_ip}:{port}...")
    await start_websocket_server(
        target_ip=target_ip,
        port=port,
        action=ServerTasks
    )