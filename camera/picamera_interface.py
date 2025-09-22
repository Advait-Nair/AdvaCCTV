from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import PyavOutput
from picamera2 import Picamera2
from utils.config import clip_size, properties_cfg
import datetime
import asyncio

cam = Picamera2()
vcfg = cam.create_video_configuration({'size': (1920, 1080), 'format': 'YUV420'})
cam.configure(vcfg)

encoder = H264Encoder(bitrate=10000000)
encoder.audio = False

DEFAULT_CLIP_LENGTH = clip_size or 60
VIDEO_SAVE_PATH = properties_cfg.get('video_save_path') or './videos'

def vname(length:int=DEFAULT_CLIP_LENGTH, suffix=".h264"):
    now = datetime.datetime.now()
    timestamp = now.strftime("%d %b %Y at %H%M")
    return f"{timestamp} {length}s" + suffix

async def clip_video(
    length=DEFAULT_CLIP_LENGTH,
    quality=Quality.HIGH,
    output=vname(suffix='.mp4')
):
    pyavout = PyavOutput(VIDEO_SAVE_PATH + '/' + output)
    cam.start_recording(encoder, pyavout, quality=quality)
    print(f"Recording '{output}'")
    await asyncio.sleep(length)
    cam.stop_recording()
    print(f"Saved '{output}' to '{VIDEO_SAVE_PATH}'")
    return VIDEO_SAVE_PATH, output
