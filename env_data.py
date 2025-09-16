from dotenv import load_dotenv
from os import environ
load_dotenv()

target_ip = environ.get('server_ip')
port = environ.get('server_port')
server_mode = environ.get("server_mode")

