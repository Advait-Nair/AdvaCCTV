"""Websockets handler
"""

from collections.abc import Callable

import asyncio

from websockets import ClientConnection, ServerConnection
from websockets.asyncio.server import serve
from websockets.asyncio.client import connect


async def start_websocket_server(target_ip:str, port:int, action:Callable[[ServerConnection], None]):

    async def _wsmain():
        async with serve(action, target_ip, port) as server:
            await server.serve_forever()
    
    asyncio.run(_wsmain())


async def start_client(target_ip:str, port:int, action:Callable[[ClientConnection], None]):
    async def _wsclient():
        async with connect(f"ws://{target_ip}:{port}") as websocket:
            action(websocket)
    
    asyncio.run(_wsclient())