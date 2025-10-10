"""
Adva Custom-Built Webserver Tag & Queue System

Queue and collect tagged chunks of data

"""

from websockets import ClientConnection
from typing import Union # We use Union because Picamera2 + dependencies is compiled to run on Python 3.9... which doesnt have the pipe (3.10+)
from utils.log import log, error
from enum import Enum
from utils.generic import get_enum_key, GetKey, get_ip
import json
import asyncio



class ProtoTags(Enum):
    EMPTY = 0
    RECV_LIVE = 1
    RECV_FILE = 2
    OLD_RECORDING = 3
    META = 4
    ID_HANDSHAKE = 5  # WS IP and Identity Handshake
    ACK = 6 # Acknowledge
    MSG = 7 # Message
    UNK = 8
    JDICT = 9 # dictionary

class EndpointMode(Enum):
    DAEMON = 0
    SERVER = 1


separator = b'/'
bn = 4

def apply_packet_tag(data:Union[str,bytes], tag:ProtoTags, encoding='utf-8') -> bytes:
    """Tag data with a simple header to indicate it's a string."""
    try:
        tagged = tag.value.to_bytes(bn, byteorder='big') + separator + (data if type(data) == bytes else data.encode(encoding=encoding))
        return tagged
    except Exception as e: error(f'Cannot inscribe prototag!\n\n{e}\n')

def get_packet_tag(data:bytes) -> ProtoTags:
    if type(data) != bytes: error('Non-bytes passed to get_packet_tag')
    """Extract the tag from the data."""
    # if data[ptaglen] != separator: return ProtoTags.EMPTY
    try:
        ptri = data.find(separator)
        tag:bytes = data[:ptri]
        return ProtoTags(int.from_bytes(tag, byteorder='big'))
    except Exception as e:
        error(f'Cannot extract prototag!\n\n{e}\n')
        return ProtoTags.EMPTY

def get_packet_data(data:bytes, format=str) -> Union[str, bytes]:
    """Extract the tag from the data."""
    # if data[ptaglen] != separator: return (ProtoTags.EMPTY,data)
    try:
        return format(data[(data.find(separator)+1):])
    except Exception as e: error(f'Cannot separate data from prototag!\n\n{e}\n')

def display_handshake_success(hs_info_dict:dict):
    mode = EndpointMode(hs_info_dict.get('mode') or 0)
    ip = hs_info_dict.get('ip') or 'indeterminate_ip'
    fstring = f"{mode.name} @ {ip}"
    log(fstring, 'handshake success')



class DataInstrument:
    def __init__(self, data:Union[str,bytes], ptag=None, encoding='utf-8'):
        """All data inputted must be given a tag with the ptag property if not already provided."""
        encoded_bytes = data.encode(encoding=encoding) if type(data) == str else data

        if ptag:
            self.data = data
            # self.data = apply_packet_tag(data=encoded, tag=ptag)
            self.tag = ptag
            # self.data_only = data
            return
        

        self.data = get_packet_data(data=encoded_bytes, format=bytes)
        self.tag = get_packet_tag(data=encoded_bytes)
        # self.data = data
        # self.data = lambda: apply_packet_tag(self.data_only, tag=self.get_tag())

    
    @classmethod
    def filter_din_by_tag(cls, din, applied_filters:list, empty_allows_all=False) -> bool:
        return din.get_tag() in applied_filters if len(applied_filters) > 0 else lambda _: (True if empty_allows_all else False)
    
    def __str__(self, encoding='utf-8'):
        return self.data.decode(encoding=encoding) if type(self.data) == bytes else self.data

    def tostr(self, encoding='utf-8', tag=False) -> str:
        """Returns str excluding tag. To include the tag, add argument tag=True"""
        if tag:
            return (self.tag + '/' + self.__str__(encoding=encoding))
            # error('tostr(tag=) has been deprecated. All data over the websocket is to be sent exclusively over binary.')
            # tagged = str(self.get_tag().value.to_bytes(bn, byteorder='big')) + separator.decode() + self.data.decode(encoding=encoding) if type(self.data) == bytes else self.data
            # print('TAGGED', tagged, self.get_tag().value.to_bytes(bn, byteorder='big'))
            # return str(self.get_tag().value.to_bytes(bn, byteorder='big')) + separator.decode() + self.data.decode(encoding=encoding) if type(self.data) == bytes else self.data
            
        return self.__str__(encoding=encoding)
    
    def tobin (self, encoding='utf-8') -> bytes:
        """Returns bytes including the tag."""
        return apply_packet_tag(data=self.data, tag=self.tag, encoding=encoding)
        # return self.tag.encode(encoding=encoding) + self.data.encode(encoding=encoding) if type(self.data) != bytes else self.data
    
    def todict (self, encoding='utf-8') -> dict:
        if not self.filter_din_by_tag(din=self, applied_filters=[ProtoTags.JDICT, ProtoTags.ID_HANDSHAKE]): log('DataInstrument().todict called on instrument without JDICT or ID_HANDSHAKE tag! Unexpected behaviour is likely.')
        try: return json.loads(self.tostr(encoding=encoding))
        except Exception as e:
            error(e)
            return {}

    def get_tag (self) -> ProtoTags:
        return self.tag
        # return get_packet_tag(bytes(self.data))

# class Packet:
#     def __init__(self, tag:ProtoTags, data:DataInstrument):
#         self.tag = tag
#         self.din = data



class WSQueue:
    """
    ```python
    # DO NOT FORGET TO HOOK WSQueue and Sender in a separate coroutine!
    ack_empty = WSQueue()
    ack_empty.add_filters([ProtoTags.ACK, ProtoTags.EMPTY])
    ack_empty.trigger(lambda din, sq: log('ACK/EMPTY >>', din.tostr()))
    # print('ack_empty',ack_empty)

    jdict = WSQueue()
    ```
    """
    master_queue:list[DataInstrument] = []
    ws:ClientConnection = False
    subqueue_filter:list[ProtoTags] = []

    _subcallers = []

    @classmethod
    def _g(cls):
        try: return cls.ws
        except Exception as e: error(e)

    @classmethod
    async def hook(cls, ws:ClientConnection): 
        cls.ws = ws

        await cls.auto_log_messages(state=True)
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=2)
                # All data received is expected to have a packet tag.
                din = DataInstrument(msg)
                print(din.get_tag(), din, 'received')
                cls.master_queue.append(din)
                for f in cls._subcallers:
                    f(din)
            except Exception as e:
                error(e)
            await asyncio.sleep(1)
        # async for msg in ws:
        #     # All data received is expected to have a packet tag.
        #     din = DataInstrument(msg)
        #     cls.master_queue.append(din)
        #     for f in cls._subcallers:
        #         f(din)
        #     asyncio.sleep(2)

    

    @classmethod
    def abort_not_hooked(cls):
        return not cls.ws
    

    @classmethod
    async def auto_log_messages(cls, state=True, log_all_with_tags:list[DataInstrument] = [ProtoTags.MSG], mute_handshake=False):
        def out(din: DataInstrument):
            if din.get_tag() == ProtoTags.ID_HANDSHAKE and not mute_handshake:
                display_handshake_success(din.todict())
                return
            
            if DataInstrument.filter_din_by_tag(din=din, applied_filters=log_all_with_tags, empty_allows_all=True):
                log(din.tostr())
            
        if state: WSQueue._subcallers.append(out)
        if not state: WSQueue._subcallers.pop(out)


    def __init__(self, subqueue: list[DataInstrument]=[]):
        self.subqueue = subqueue
        self.subqueue_filter = []
        self._filter_ = lambda din: DataInstrument.filter_din_by_tag(din=din, applied_filters=self.subqueue_filter, empty_allows_all=True)
        # self._filter_ = lambda din: din.get_tag() in self.subqueue_filter if len(self.subqueue_filter) > 0 else lambda _: True
        WSQueue._subcallers.append(
            lambda din: self.subqueue.append(din) if self._filter_(din) else False
        )


    
    def add_filters(self, tags: list[ProtoTags] = []):
        """As the WSQueue gets more messages, we can filter by tags."""
        if type(tags) == list:
            for tag in tags: self.subqueue_filter.append(tag)
            return
        self.subqueue_filter.append(tags)
    
    def remove_filters(self, tags: list[ProtoTags] = []):
        """As the WSQueue gets more messages, we can filter by tags."""
        if type(tags) == list:
            for tag in tags: self.subqueue_filter.pop(tag)
            return
        self.subqueue_filter.pop(tags)

    def reset_filters(self):
        self.subqueue_filter = []



    trigger_id_maps = {}

    def trigger(self, fn):
        applied_fn = lambda din: fn(din, self.subqueue) if DataInstrument.filter_din_by_tag(din=din, applied_filters=self.subqueue_filter) else None
        WSQueue._subcallers.append(applied_fn)
        WSQueue.trigger_id_maps[id(fn)] = id(applied_fn)
        
    
    def kill_trigger(self, fn):
        afn_to_kill = WSQueue.trigger_id_maps.get(id(fn), False)
        if not afn_to_kill:
            log('WSQueue().kill_trigger: fn to kill has not been recognised.')
            return

        for f in WSQueue._subcallers:
            if id(f) == afn_to_kill:
                WSQueue._subcallers.pop(f)
                break
        


class Sender:

    ws:ClientConnection = None
    handshake_sent = False

    @classmethod
    def hook(cls, ws:ClientConnection):
        cls.ws = ws

    
    @classmethod
    def abort_not_hooked(cls):
        return not cls.ws

    @classmethod
    async def send_din(cls, din: DataInstrument):
        await cls.ws.send(din.tobin())
    
    @classmethod
    async def send(cls, data:Union[str, bytes], tag: ProtoTags):
        din = DataInstrument(data=data, ptag=tag)
        # print('sending',din)
        await cls.ws.send(din.tobin())
    

    @classmethod
    async def send_dict(cls, d:dict, tag: ProtoTags = ProtoTags.JDICT):
        packaged_data = DataInstrument(json.dumps(d), ptag=tag)
        # print('sending jdict')
        await cls.ws.send(packaged_data.tobin())

    
    @classmethod
    async def send_large_buffer(cls, large_buffer:list[bytes], tag: ProtoTags = ProtoTags.JDICT):
        await cls.ws.send(DataInstrument(data=frame, ptag=tag).tobin() for frame in large_buffer)
    
    @classmethod
    async def send_msg(cls, msg:str):
        await cls.ws.send(DataInstrument(msg, ptag=ProtoTags.MSG).tobin())
    
    @classmethod
    async def handshake(cls, report_as=EndpointMode.DAEMON, force_handshake=False):
        if not force_handshake and cls.handshake_sent: return
        client_identity = {
            'ip': get_ip(),
            'mode': report_as.value
        }
        await cls.send_dict(client_identity, tag=ProtoTags.ID_HANDSHAKE)
        cls.handshake_sent = True