# Update the whole program on a commit.

from utils.config import properties_cfg
from asyncio import sleep
import subprocess
check_rate = properties_cfg.get("update_check_rate")

def update():
    subprocess.run("git pull".split(' '))
    subprocess.run("python3.12 .".split(' '))
    exit(0)

    # subprocess.run("git pull \n && python3.12 .".split(' '))

def check_update():
    print("Running update check...")
    subprocess.run("git remote update".split(' '), stdout=subprocess.DEVNULL)
    needs_update = not "up to date" in subprocess.run("git status | grep \"up to date\"".split(' '),encoding="utf-8", stdout=subprocess.PIPE).stdout
    
    if needs_update:
        print("\n\nPreparing update...\n")
        update()




async def UpdaterCycle():
    while True:
        check_update()
        await sleep(float(check_rate))