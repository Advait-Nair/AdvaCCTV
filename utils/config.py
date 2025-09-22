# from dotenv import load_dotenv
# from os import environ
# load_dotenv()

# target_ip = environ.get('server_ip')
# port = environ.get('server_port')
# server_mode = environ.get("server_mode")



import tomllib
import os

from utils.cfg_path import CONFIG_PATH


with open(CONFIG_PATH, "rb") as f:
    config_data = tomllib.load(f)

    server_cfg:dict = config_data.get("server")
    properties_cfg:dict = config_data.get("properties")
    flags_cfg:dict = config_data.get("flags")

    target_ip = server_cfg.get("server_ip")
    port = server_cfg.get("server_port")
    server_mode = flags_cfg.get("server_mode")
    clip_size = server_cfg.get("capture_clip_length")


