# Update the whole program on a commit.

from utils.config import properties_cfg
from asyncio import sleep
import subprocess
from utils.log import log
import os


check_rate = properties_cfg.get("update_check_rate")
from utils.config import CONFIG_PATH
def update():
    # Save toml file

    # toml = ""
    # with open(CONFIG_PATH, 'r') as f:
    #     toml = f.read()
    #     f.close()
    # Run git stash to save any local changes
    subprocess.run("git stash".split(' '))

    # Run git fetch to get remote changes without merging
    subprocess.run("git fetch".split(' '))

    # Create a list of files to ignore during pull
    ignore_files = ["primary.log", "config.toml"]
    for file in ignore_files:
        # Check if the file exists
        if os.path.exists(file):
            # Add to git assume-unchanged to ignore changes
            subprocess.run(f"git update-index --assume-unchanged {file}".split(' '))
    subprocess.run("git pull".split(' '))
    subprocess.run(f"pip3.12 install -r requirements.txt{" --break-system-packages" if os.path.exists('./.venv') else ''}".split(''))

    # with open(CONFIG_PATH, 'w') as fw:
    #     fw.write(toml)
    #     fw.close()

    subprocess.run("python3.12 .".split(' '))
    exit(0)

    # subprocess.run("git pull \n && python3.12 .".split(' '))

def check_update():
    log("Running update check...")
    subprocess.run("git remote update".split(' '), stdout=subprocess.DEVNULL)
    needs_update = not "up to date" in subprocess.run("git status | grep \"up to date\"".split(' '),encoding="utf-8", stdout=subprocess.PIPE).stdout
    
    if needs_update:
        log("\n\nPreparing update...\n")
        try: update()
        except Exception as e:
            log("Update failed! Error below:")
            log(e)
            print('\n'*10)
            subprocess.run("git reset --hard HEAD".split(' '))
            subprocess.run("git clean -f".split(' '))
            subprocess.run("git pull".split(' '))
            subprocess.run("python3.12 .".split(' '))
            exit(1)
            return
        
        log("Update complete! The server will auto-restart.")
        print('\n'*10)




async def UpdaterCycle():
    while True:
        check_update()
        await sleep(float(check_rate))