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

from endpoints.server import ServerMain
from endpoints.daemon import DaemonMain
from error.output import output, CodeType
import os
import sys
from utils.config import *
from asyncio import run, gather
from utils.updater import UpdaterCycle
from utils.quick_setup import QuickSetup
from utils.log import log, instantiate_log_session
from utils.systemctl_restarter import Restarter
import subprocess
import tracemalloc
tracemalloc.start()


# Python Version Information - Dependency Debug, Runtime Info
print ('\n'*11)
print (sys.version,'\n__\n')


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
    

if __name__ == "__main__":
    if "setup" in sys.argv:
        QuickSetup()
        subprocess.run("python3.12 .".split(' '))

    if "update" in sys.argv:
        subprocess.run(["git", "pull"])
        exit(1)
    if "autostart-set" in sys.argv:
        
        Restarter()
        exit(1)

    # Decide whether this is daemon or server-side
    Main, locflag = get_loc()

    log(f"{target_ip}:{port} | {locflag}")

    try:
        instantiate_log_session()
        async def dual(): await gather(Main(), UpdaterCycle())
        run(dual())

        # run(Main())
        # run(UpdaterCycle())
    
    except KeyboardInterrupt:
        log("\n\nACCTV has been manually aborted.\n")
        exit(1)
    except Exception as e:
        output(title="A fatal Main () error has occurred!", msg=f"This is on the {locflag}.", ctype=CodeType.Error, code=0, e=e)
        log(f"\n\nA fatal Main () error has occurred! This is on the {locflag}.\n")
        subprocess.run('python3.12 .'.split(' '))
        exit(1)

log("\nCCTV Daemon/Server has exited.")