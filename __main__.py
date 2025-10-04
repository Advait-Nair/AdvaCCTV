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
from utils.log import log, instantiate_log_session, error
from utils.systemctl_restarter import Restarter
from utils.generic import restart_self, runcmd, get_ip

import tracemalloc
tracemalloc.start()


VIDEO_SAVE_PATH = properties_cfg.get("video_save_path") or "./videos"
# If video directory is missing, create it
if not os.path.exists(VIDEO_SAVE_PATH):
    os.makedirs(VIDEO_SAVE_PATH)


# Python Version Information - Dependency Debug, Runtime Info
print ('\n'*3)

print("""
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

    argvj=' '.join(sys.argv)
    if '-t' in argvj:
        global retry_timeout
        try: retry_timeout = int(argvj.split('-t')[1].strip().split(' ')[0])
        except: retry_timeout = 5
        # acctv arg1 arg2 -t 3 arg4
        #  3 arg4
        # [3, arg4]

    if "setup" in sys.argv:
        QuickSetup()
        restart_self()
    
    if "cmerge" in sys.argv:
        from utils.updater import merge_config_base
        merge_config_base()
        exit(1)

    if "update" in sys.argv:
        runcmd('git pull')
        exit(1)
    
    if "logflush" in sys.argv:
        f = open('primary.log', 'w')
        f.close()
        exit(1)
    

    if "autostart-set" in sys.argv:
        
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
            # print('sc',sc)
            run(sc())
            return
        
        from endpoints.daemon import closer as dc
        # print('dc',dc)
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