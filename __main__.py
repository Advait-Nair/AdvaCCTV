"""
                                                                                         
                                                                                                    
                           ::#@@@@@@@@#.                                            
                          -@%-%@@@@@@@@@.                                           
                         +@@@%:%@@@@@@@@@-                                          
                       .*@@@@@@-*@@@@@@@@@=                                         
                      .@@@@@@@@@++@@@@@@@@@*.                                       
                     =@@@@@@@@@%. :@@@@@@@@@#.                                      
                    =@@@@@@@@@*    :@@@@@@@@@@:                                     
                  .#@@@@@@@@@+.     .#@@@@@@@@@-                                    
                 .%@@@@@@@@@:        .*@@@@@@@@@=                                   
                -@@@@@@@@@#:           =@@@@@@@@@*.                                 
              .+@@@@@@@@@*-=:.          -@@@@@@@@@#.                                
              #@@@@@@@@@=+@@@@@@@#*=:.   :@@@@@@@@@@:                               
            :%@@@@@@@@@-#@@@@@@@@@@@@@@@@%*=--+%@@@@@:                              
           :@@@@@@@@@#.%@@@@@@@@@@@@@@@@@@@@@@@@@%+-:-:                             
          +@@@@@@@@@#..:+%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=                            
        .*@@@@@@@@@-           :#@@@@@@@@@@@@@@@@@@@@@@@%.                          
       .@@@@@@@@@@-                   .=%@@@@@@@@@@@@@@@@%:                         
      -@@@@@@@@@@.                            .+%@@@@@@@@@@:                        
      =########+.                                     :*####-                       
                                                                                                    
      _______________________________________________________

      ADVA CCTV Daemon & Server

      Written by
        Advait Nair (Adva Software), 2025. advaitnair.org.
    
      Open-source CCTV Daemon & Server.

      This software is under the GNU GPL v3 license. Modification,
      redistribution and use is permitted given the program and/or
      its components remain open-source and are not monetised or
      paywalled in any way.

      THIS NOTICE MUST NOT BE REMOVED!

      
"""
import os
import sys
import time

from utils.mirror_logging import *

from utils.cfg_path import CONFIG_PATH
from utils.generic import runcmd, handle_kbd_int, restart_self

# If config.toml is missing, copy config_base.toml to config.toml
if not os.path.exists(CONFIG_PATH):
    if os.path.exists("config_base.toml"):
        runcmd("cp config_base.toml config.toml")
    else:
        output(title="Critical Error!", msg="Config file is missing, and config_base.toml is also missing! Please redownload the package.", ctype=CodeType.Error, code=0)
        exit(1)



from error.output import output, CodeType


from endpoints.server import ServerMain
from endpoints.daemon import DaemonMain


import sys
from utils.config import *
from asyncio import run, gather
from utils.updater import UpdaterCycle
from utils.quick_setup import QuickSetup
from utils.log import log, instantiate_log_session, error, LOG_PATH
from utils.systemctl_restarter import Restarter
from utils.generic import restart_self, runcmd, get_ip, get_build
from utils.arguments import *

import tracemalloc
tracemalloc.start()

retry_timeout = get_cli_value_arg('-t', int, 5)

VIDEO_SAVE_PATH = properties_cfg.get("video_save_path") or "./videos"
# If video directory is missing, create it
if not os.path.exists(VIDEO_SAVE_PATH):
    os.makedirs(VIDEO_SAVE_PATH)


# Python Version Information - Dependency Debug, Runtime Info
print ('\n'*3)

print(f"""
_________________________________________________________________


    Adva Software Closed Circuit Television System | advacctv
    
        A FOSS for local home CCTV solutions.
        © 2020-2025 Advait Nair, Adva Software.
      
        Visit https://advaitnair.org
    
    
    [!] Legal Disclaimer
    
    Adva CCTV is provided "as-is" and comes with
    absolutely no warranty or responsibility for any damage
    to persons, properties or entities caused by the
    improper function or utilisation of this software.
      
      
    [?] QUICK ARGUMENTS TABLE
    
    -svm                Run as server
    -dm                 Run as daemon
    
    -t <t>              Set retry timeout
                        <t: seconds>, default 5
    -ip <ipv4>          Connect to server ip
                        <ipv4: 255.255.255.255>, default
                        from config.toml
    -port <port>        Connect to server on port
                        <port: integer>, default from
                        config.toml
    -clip-length <l>    Set video clipping length for
                        the daemon
    
    
    setup           Run in setup mode
    mirrorlog       Run a live mirror stdout stream from an
                    autonomous acctv process
    cmerge          Merge contents of base and setup config
    update          Check and/or update to latest version
    flog            Flush contents of log file "{LOG_PATH}"
    autostart-set   Configure systemd to run on startup
                    (!) This is experimental.

                    
    [V] VERSION INFORMATION

    {get_build()}


    [A] RUNNING CONFIGURATION

    {'\n    '.join(flags_overview_str.split('\n')) or '\tDefault configuration'}
      
_________________________________________________________________\n\n
""")
print ('Running on',sys.version,'\n')

retry_timeout = 5

def is_server():
    # debug override
    if "-svm" in sys.argv:
      return True
    if "-dm" in sys.argv:
      return False
    
    
    return server_mode

def get_loc():
    Main = DaemonMain
    
    locflag = 'daemon'
    if is_server():
       
       # Override the ip, because how on earth would you bind to an address that's not yours? (In this circumstance)
       global target_ip
       target_ip = get_ip()

       Main = ServerMain


       locflag = 'server'
    
    return [Main, locflag]




Main, locflag = get_loc()




def main():
    global target_ip


    if is_flag_present_arg('setup'):
        QuickSetup()
        restart_self()
    elif is_flag_present_arg("cmerge"):
        from utils.updater import merge_config_base
        merge_config_base()
        exit(1)
    elif is_flag_present_arg("update"):
        runcmd('git pull')
        exit(1)
    elif is_flag_present_arg("flog"):
        f = open('primary.log', 'w')
        f.close()
        exit(1)
    if is_flag_present_arg("mirrorlog"):
        handle_kbd_int(fn=StartMirrorLogging(), suppress=True, on_ki_fn=lambda: log('Exiting live log mirror.'))
        exit(1)
    if is_flag_present_arg("autostart-set"):
        Restarter()
        exit(1)

    # Decide whether this is daemon or server-side
    

    log(f"{target_ip}:{port} | {locflag}")

    # try:
    instantiate_log_session()
    async def dual(): await gather(Main(), UpdaterCycle())
    run(dual())

    # run(Main())
    # run(UpdaterCycle())



def handle_nonstandard_exception(e):
    # output(title="A fatal Main () error has occurred!", msg=f"This is on the {locflag}.", ctype=CodeType.Error, code=0, e=e)
    # log(f"\n\nA fatal Main () error has occurred! This is on the {locflag}.\n")
    error(e)
    print('\n\n\n- - - - - - - - - | AUTO-RESTARTING | - - - - - - - - -\n')



def ki_fn_closer():
    try:
        if is_server():
            from endpoints.server import closer as sc
            run(sc())
            return
        
        from endpoints.daemon import closer as dc
        run(dc())
    except Exception as e: error(e)

def _controlled_main():
    try: handle_kbd_int(main, on_ki_fn=ki_fn_closer)
    except Exception as e:

        def on_retry():
            handle_nonstandard_exception(e)
            print(f'Applying {retry_timeout} second retry timeout.')
            time.sleep(retry_timeout)
            _controlled_main()
        
        handle_kbd_int(
            fn=on_retry,
            suppress=True
        )


if __name__ == "__main__":
    _controlled_main()