import builtins
import os
import typing
import asyncio
import time
import sys
TMP_MIRROR_LOG_PATH = ".clog.log"


open(TMP_MIRROR_LOG_PATH, 'w').close() # Flush its contents

def print(*args, **kwargs):
    """This is the standard python print function, redefined to mirror output to a temprorary location to allow mirroring."""
    builtins.print(*args, **kwargs)

    if kwargs.get('file'): del kwargs['file']
    # if not kwargs.get('sep'): kwargs['sep'] = ' '
    with open(TMP_MIRROR_LOG_PATH, 'a') as f:
        builtins.print(*args, **kwargs, file=f)
        # f.write(kwargs['sep'].join(str(arg) for arg in args))


last_line_size = 0
def _read_tmp_logfile_as_whole(f:typing.TextIO):
    global last_line_size
    lines = f.readlines()
    last_line_size = len(f.read())
    builtins.print('\n'.join(lines))

def _read_tmp_logfile_as_updated(f:typing.TextIO):
    global last_line_size
    os.system('clear')
    _read_tmp_logfile_as_whole(f)


last_modified = None
def has_file_not_changed(fpath:str):
    global last_modified
    current_modified = os.path.getmtime(fpath)
    if current_modified == last_modified:
        last_modified = current_modified
        return True
    else: return False


def StartMirrorLogging():
    """Begin a mirroring process. This is a dedicated process."""
    builtins.print('Beginning Mirror Logging...')
    with open(TMP_MIRROR_LOG_PATH, 'r') as tmp_log_f_r:
        _read_tmp_logfile_as_whole(tmp_log_f_r)
    while True:
        with open(TMP_MIRROR_LOG_PATH, 'r') as tmp_log_f_r:
            # if has_file_not_changed(TMP_MIRROR_LOG_PATH):
            #     print('filechange')
                # continue
            _read_tmp_logfile_as_updated(tmp_log_f_r)
            time.sleep(0.1)
        
    
