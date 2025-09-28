from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
from picamera2 import Picamera2
from utils.config import clip_size, properties_cfg
from utils.log import log, error
import datetime
import asyncio
from utils.generic import create_path_if_not_exists

cam = Picamera2()
vcfg = cam.create_video_configuration({'size': (1920, 1080), 'format': 'YUV420'})
cam.configure(vcfg)

encoder = H264Encoder(bitrate=10000000)
encoder.audio = False

DEFAULT_CLIP_LENGTH = clip_size or 60
VIDEO_SAVE_PATH = properties_cfg.get('video_save_path') or './videos'



create_path_if_not_exists(VIDEO_SAVE_PATH)

def vname(length:int=DEFAULT_CLIP_LENGTH, suffix=".h264"):
    now = datetime.datetime.now()
    timestamp = now.strftime("%d_%b_%Y_at_%H%M%S")
    return f"{timestamp}__{length}s" + suffix

async def clip_video(
    length=DEFAULT_CLIP_LENGTH,
    quality=Quality.HIGH,
    output=vname(suffix='.mp4')
):
    try:
        ffmout = FfmpegOutput(VIDEO_SAVE_PATH + '/' + output)
        cam.start_recording(encoder, ffmout, quality=quality)
        log(f"Recording '{output}'")
        await asyncio.sleep(length)
        cam.stop_recording()
        log(f"Saved '{output}' to '{VIDEO_SAVE_PATH}'")
    except Exception as e:
        error(f"Error recording {output}:", e)

    return VIDEO_SAVE_PATH, output

