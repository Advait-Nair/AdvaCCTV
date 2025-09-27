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
from utils.generic import restart_self, runcmd

import tracemalloc
tracemalloc.start()


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


def is_server():
    # debug override
    if "-svm" in sys.argv:
      return True
    
    return server_mode

def get_loc():
    Main = DaemonMain
    
    locflag = 'daemon'
    if is_server():
       Main = ServerMain
       locflag = 'server'
    
    return [Main, locflag]




Main, locflag = get_loc()

def main():

    if "setup" in sys.argv:
        QuickSetup()
        restart_self()

    if "update" in sys.argv:
        runcmd('git pull')
        exit(1)
    
    if "logflush" in sys.argv:
        f = open('primary.log', 'w')
        f.close()
        exit()
    

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




def _controlled_main():
    try: handle_kbd_int(main)
    except Exception as e:

        def on_retry():
            handle_nonstandard_exception(e)
            _controlled_main()
        
        handle_kbd_int(
            fn=on_retry,
            suppress=True
        )


if __name__ == "__main__":
    _controlled_main()