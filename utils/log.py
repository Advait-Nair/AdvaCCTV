import datetime
from utils.config import properties_cfg

max_log_size = properties_cfg.get("max_log_size")
delete_top_n_lines_on_log_full = properties_cfg.get("delete_top_n_lines_on_log_full")

LOG_PATH = "primary.log"

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
    timestamp = ts()
    print(timestamp, *args, **kwargs)
    recorded_size = 0
    with open(LOG_PATH, "r+") as f:
        print(timestamp, *args, **kwargs, file=f)
        recorded_size = len(f.readlines())

        if recorded_size > max_log_size:
            removeTopLines(LOG_PATH, delete_top_n_lines_on_log_full)

        f.close()
    