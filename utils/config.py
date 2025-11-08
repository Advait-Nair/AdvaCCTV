# from dotenv import load_dotenv
# from os import environ
# load_dotenv()

# target_ip = environ.get('server_ip')
# port = environ.get('server_port')
# server_mode = environ.get("server_mode")



try: import tomllib
except ModuleNotFoundError: import pip._vendor.tomli as tomllib
from utils.mirror_logging import *
from utils.cfg_path import CONFIG_PATH
from utils.arguments import get_cli_value_arg

try:
    with open(CONFIG_PATH, "rb") as f:
        config_data = tomllib.load(f)

        server_cfg:dict = config_data.get("server")
        properties_cfg:dict = config_data.get("properties")
        flags_cfg:dict = config_data.get("flags")

        # sc_ip = server_cfg.get("server_ip")
        target_ip = get_cli_value_arg('-ip', str, server_cfg.get("server_ip"))
        # if target_ip != sc_ip:
        #     print('Running with target server IP set to',target_ip,'instead of',sc_ip)

        port = get_cli_value_arg('-port', str, server_cfg.get("server_port"))
        # port = server_cfg.get("server_port")

        server_mode = flags_cfg.get("server_mode")
        
        # clip_size = properties_cfg.get("capture_clip_length")
        clip_size = get_cli_value_arg('-clip-length', float, properties_cfg.get("capture_clip_length"))

        pyv = properties_cfg.get("pyv") or "3.12"

except:
    print("Cannot parse config.toml - your config file might be corrupt!\n\t1. Run cat config.toml and check the TOML follows specification.\n\t2. Re-run acctv setup to reset the configuration file.\n\t3. Run acctv update. If this fails, manually git pull the latest version, which may fix your issue.",fatal=True)