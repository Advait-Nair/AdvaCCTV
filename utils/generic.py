

import os
import subprocess
import sys
from utils.log import log


def create_path_if_not_exists(path:str):
    if not os.path.exists(path):
        os.makedirs(path)


def runcmd(s:str, *args, **kwargs):
    return subprocess.run(s.split(' '), *args, **kwargs)

def restart_self():
    runcmd("python3.12 .")


def handle_kbd_int(fn, suppress=False):
    try:
        fn()
    except KeyboardInterrupt:
        if suppress: return

        print('\n'*2)
        log("Adva CCTV has been manually aborted.\n")
        sys.exit(130)