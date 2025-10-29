"""Websockets handler
"""
from utils.mirror_logging import *

from collections.abc import Callable

import asyncio

from websockets import ClientConnection, ServerConnection
from websockets.asyncio.server import serve
from websockets.asyncio.client import connect
from utils.generic import megabytes_to_pow2_bytes
from utils.log import log, error


# TODO tweak for perf and ram optimisations
CONN_KWARGS = {
    "max_size": megabytes_to_pow2_bytes(50),
    "max_queue": 64,
    "write_limit": megabytes_to_pow2_bytes(1),
}

async def start_websocket_server(target_ip:str, port:int, action:Callable[[ServerConnection], None]):

    async def _wsmain():
        async with serve(action, target_ip, port) as server:
            await server.serve_forever()

        # async for server in serve(action, target_ip, port):
        #     await server.serve_forever()
    
    # asyncio.run(_wsmain())
    await _wsmain()


async def start_client(target_ip:str, port:int, action:Callable[[ClientConnection], None]):
    async def _wsclient():
        # async with connect(f"ws://{target_ip}:{port}") as websocket:
            # await action(websocket)
        async for websocket in connect(f"ws://{target_ip}:{port}", **CONN_KWARGS):
            try:
                await action(websocket)
            except Exception as e:
                error(e)
                log('Restarting client...')
                continue
    
    # asyncio.run(_wsclient())
    await _wsclient()