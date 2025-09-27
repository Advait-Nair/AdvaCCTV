import datetime
from utils.config import properties_cfg
import os

max_log_size:int = properties_cfg.get("max_log_size") or 5000
delete_top_n_lines_on_log_full = properties_cfg.get("delete_top_n_lines_on_log_full")

LOG_PATH = "primary.log"

def ensure_log_file_exists():
    if not os.path.exists(LOG_PATH):
        # Create the directory if it doesn't exist
        log_dir = os.path.dirname(LOG_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        # Create the log file
        with open(LOG_PATH, 'w') as f:
            f.close()


def ts():
    now = datetime.datetime.now()
    return now.strftime("[%d %b %Y at %H:%M:%S]")

def instantiate_log_session():
    with open(LOG_PATH, "a") as f:
        print("\n\n"+"="*20+f" Log Commencing {ts()} "+"="*20+"\n\n", file=f)
        f.close()

def removeTopLines(file_path, num_lines):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        file.writelines(lines[num_lines:])
    

def log(*args, **kwargs):
    ensure_log_file_exists()
    timestamp = ts()
    print(timestamp, *args, **kwargs)
    recorded_size = 0
    with open(LOG_PATH, "a+") as f:
        print(timestamp, *args, **kwargs, file=f)
        recorded_size = len(f.readlines())

        if recorded_size > max_log_size:
            removeTopLines(LOG_PATH, delete_top_n_lines_on_log_full)

        f.close()

def error(*args, **kwargs):
    is_fatal = kwargs.get('fatal', False)
    fatal = " FATAL!" if is_fatal else ""
    log(f'[[ ERR ! ]]{fatal}',*args, **kwargs)
    