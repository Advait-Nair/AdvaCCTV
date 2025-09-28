# Update the whole program on a commit.

from utils.config import properties_cfg, pyv
from asyncio import sleep
import subprocess
from utils.log import log
import os
from utils.generic import restart_self, runcmd

check_rate = properties_cfg.get("update_check_rate")
from utils.config import CONFIG_PATH



def merge_config_base():
    # Merge config_base.toml into config.toml without overwriting existing keys
    if not os.path.exists("config_base.toml"):
        return
    

    
    # read existing config
    with open(CONFIG_PATH, 'r') as f:
        toml = f.readlines()
        f.close()
    
    # Create a dictionary of existing keys in a flattened format in config.toml
    existing_keys = {}
    for line in toml:
        if '=' in line:
            key, value = line.split('=')
            existing_keys[key.strip()] = value.strip()

    # Copy over the new base to the existing file
    runcmd("cp config_base.toml config.toml")

    # Run through the new one
        # read base config - the latest is in this
    modified_buffer = ""
    with open("config_base.toml", 'r') as f:
        base_toml = f.readlines()
        for bln in base_toml:
            sub_buffer = bln
            if '=' in bln:
                k = bln.split('=')[0].strip()
                if existing_keys[k]:
                    sub_buffer = f"{k}={existing_keys[k]}"
        
            modified_buffer += sub_buffer + '\n'



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
    # bsp = " --break-system-packages" if os.path.exists('./.venv') else ''
    # log(f"Installing dependencies using pip{pyv}{bsp}...")
    # runcmd(f"pip{pyv} install -r requirements.txt{bsp}".split(''))

    # with open(CONFIG_PATH, 'w') as fw:
    #     fw.write(toml)
    #     fw.close()

    
    restart_self()




def check_update():
    print("Running update check...", end=" ")
    runcmd("git remote update", stdout=subprocess.DEVNULL)
    needs_update = not "up to date" in runcmd("git status | grep \"up to date\"",encoding="utf-8", stdout=subprocess.PIPE).stdout
    
    if needs_update:
        print("\n\n\nPreparing update...\n")
        try:
            update()
            # merge_config_base()
        except Exception as e:
            log("Update failed! Error below:")
            log(e)
            print('\n'*10)
            # runcmd("git reset --hard HEAD")
            # runcmd("git clean -f")
            # runcmd("git pull")
            # merge_config_base()
            restart_self()
            exit(1)
            return
        
        merge_config_base()
        log("Update complete! The server will auto-restart.")
        print('\n'*10)

    print("No update found.")


async def UpdaterCycle():
    while True:
        check_update()
        await sleep(float(check_rate))