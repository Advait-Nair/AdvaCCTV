from websockets import ClientConnection
from utils.log import log, error
from enum import Enum
from utils.generic import get_enum_key, GetKey, get_ip
import json




class StateFlags(Enum):
    EMPTY = 0
    RECV_LIVE = 1
    RECV_FILE = 2
    OLD_RECORDING = 3
    META = 4
    WS_HANDSHAKE = 5  # WS Handshake
    ACK = 6 # Acknowledge
    MSG = 7 # Message
    INITIAL = 8

class EndpointMode(Enum):
    DAEMON = 0
    SERVER = 1


async def send_flag_out(ws:ClientConnection, flag:int) -> bool:
    """Send a flag over - this is known as flagging out."""
    cflag = StateFlags(flag)
    try:
        await ws.send(cflag.value.to_bytes(8, byteorder='big'))
        log(f'FLAG_OUT {cflag.name}')
        return True
    except Exception as e: error(f'Cannot flag out {cflag.name}!\n\n{e}\n')
    return False
    

async def get_flag_in(ws:ClientConnection) -> StateFlags:
    """Interpret and return the activated flag - this is known as flagging in. We send flags in so that the receiving end knows which function or flow should trigger."""
    try:
        data = await ws.recv()
        flag_enum = int.from_bytes(data, 'big')
        log(f'FLAG_IN {StateFlags(flag_enum).name}')
        return StateFlags(flag_enum)
    except Exception as e: error(f'Cannot flag in!\n\n{e}\n')
    return StateFlags.EMPTY

async def ws_send_dict(ws:ClientConnection, d:dict):
    await ws.send(json.dumps(d))

async def ws_get_dict(ws:ClientConnection) -> dict:
    try:
        d = await ws.recv()
        return json.loads(d)
    except:
        error('Expecting DICT')
    return {}

async def handshake_success(hs_info_dict:dict):
    mode = EndpointMode(hs_info_dict.get('mode') or 0)
    ip = hs_info_dict.get('ip') or 'indeterminate_ip'
    fstring = f"{mode.name} @ {ip}"
    log(fstring, 'handshake success')

async def send_daemon_handshake(ws:ClientConnection):
    """Handshake flow for the daemon to use."""
    try:
        await send_flag_out(ws, StateFlags.WS_HANDSHAKE)
        await ws_send_dict(ws, {
            'ip': get_ip(),
            'mode': EndpointMode.DAEMON.value
        })
        server_hs_info_dict = await ws_get_dict(ws)
        await handshake_success(hs_info_dict=server_hs_info_dict)
    except Exception as e: error(f'Cannot send daemon handshake!\n\n{e}\n')


async def handle_server_handshake(ws:ClientConnection):
    """Handshake response for the server to use"""
    try:
        hs_flag = await get_flag_in(ws)

        if hs_flag != StateFlags.WS_HANDSHAKE: return # This is not the request we are attempting to handle

        daemon_info_dict = await ws_get_dict(ws)
        await handshake_success(hs_info_dict=daemon_info_dict)

        # Send the server's info back
        await ws_send_dict(ws, {
            'ip': get_ip(),
            'mode': EndpointMode.SERVER.value
        })
    except Exception as e: error(f'Cannot handle daemon handshake as server!\n\n{e}\n')

async def send_filestream_from_fs(ws:ClientConnection, file_location:str, chunk_size:int=5000):
    """Send a continuous set of packets that will form a file."""
    try:
        with open(file_location, 'rb') as fb:
            s_no = 0
            while segment := fb.read1(chunk_size):
                s_no += 1
                log(f'Sending {len(segment)} bytes as Segment {s_no}')
                await ws.send(segment)
    except Exception as e: error(f'Cannot send filestream from local FS!\n\n{e}\n')

async def recv_filestream(ws:ClientConnection, writes_to = None):
    try:
        if writes_to:
            with open(writes_to, 'wb') as writeloc:
                s_no = 0
                async for message in ws:
                    log(f'Received and writing {len(message)} bytes as Segment {s_no}')
                    writeloc.write(message)
            return True
        

        ram_buffer = bytearray()
        async for message in ws:
            ram_buffer.extend(message)

        return ram_buffer
    except Exception as e:
        error(f'Cannot receive filestream!\n\n{e}\n')
        return False