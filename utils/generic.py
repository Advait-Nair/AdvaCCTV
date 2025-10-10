

import os
import subprocess
import sys
import socket
import datetime

def create_path_if_not_exists(path:str):
    if not os.path.exists(path):
        os.makedirs(path)


def runcmd(s:str, *args, **kwargs):
    return subprocess.run(s.split(' '), *args, **kwargs)


def get_build():
    try:
        # Get the git commit hash
        hashno = runcmd("git rev-parse --short HEAD", capture_output=True, text=True).stdout.strip()
        # Get the git commit number
        buildno = runcmd("git rev-list --count main", capture_output=True, text=True).stdout.strip()
        # Get date of latest commit and format like time.strftime("[%d %b %Y at %H:%M:%S]")
        # Get date of latest commit
        date = runcmd("git show -s --format=%ci HEAD", capture_output=True, text=True).stdout.strip()
        # Convert to datetime and format
        commit_date = datetime.datetime.fromisoformat(date.replace(' ', 'T', 1))
        formatted_date = commit_date.strftime("released on %d %b %Y at %H:%M")
        return f"acctv build {buildno} ({hashno}), {formatted_date}"
    except Exception:
        return "unknown"

def restart_self():
    # Kill the current process and start a new one
    python_executable = sys.executable
    script_path = os.path.abspath(".")
    os.execl(python_executable, python_executable, script_path)


def handle_kbd_int(fn, suppress=False, on_ki_fn=lambda: None):
    from utils.log import log
    try:
        fn()
    except KeyboardInterrupt:
        on_ki_fn()
        if suppress: return

        print('\n'*2)
        log("Adva CCTV has been manually aborted.\n")
        sys.exit(130)


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return 'indeterminate_ip'

def get_enum_key(enum, v):
    return next((name for name, value in enum.__members__.items() if value.value == v), None)

class GetKey:
    def key(self, v): get_enum_key(self, v)

