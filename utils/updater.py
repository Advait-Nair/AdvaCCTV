# Update the whole program on a commit.

from utils.config import properties_cfg
from asyncio import sleep
import subprocess
from utils.log import log
import os
from utils.generic import restart_self, runcmd

check_rate = properties_cfg.get("update_check_rate")
from utils.config import CONFIG_PATH
def update():
    # Save toml file

    # toml = ""
    # with open(CONFIG_PATH, 'r') as f:
    #     toml = f.read()
    #     f.close()
    # Run git stash to save any local changes
    runcmd("git stash")

    # Run git fetch to get remote changes without merging
    runcmd("git fetch")

    # Create a list of files to ignore during pull
    ignore_files = ["primary.log", "config.toml"]
    for file in ignore_files:
        # Check if the file exists
        if os.path.exists(file):
            # Add to git assume-unchanged to ignore changes
            runcmd(f"git update-index --assume-unchanged {file}")
    runcmd("git pull")
    runcmd(f"pip3.12 install -r requirements.txt{" --break-system-packages" if os.path.exists('./.venv') else ''}".split(''))

    # with open(CONFIG_PATH, 'w') as fw:
    #     fw.write(toml)
    #     fw.close()

    restart_self()
    exit(0)

    # runcmd("git pull \n && python3.12 .")

def check_update():
    log("Running update check...")
    runcmd("git remote update", stdout=subprocess.DEVNULL)
    needs_update = not "up to date" in runcmd("git status | grep \"up to date\"",encoding="utf-8", stdout=subprocess.PIPE).stdout
    
    if needs_update:
        log("\n\nPreparing update...\n")
        try: update()
        except Exception as e:
            log("Update failed! Error below:")
            log(e)
            print('\n'*10)
            runcmd("git reset --hard HEAD")
            runcmd("git clean -f")
            runcmd("git pull")
            restart_self()
            exit(1)
            return
        
        log("Update complete! The server will auto-restart.")
        print('\n'*10)




async def UpdaterCycle():
    while True:
        check_update()
        await sleep(float(check_rate))