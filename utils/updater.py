# Update the whole program on a commit.

from utils.config import properties_cfg
from asyncio import sleep
import subprocess
update_time = properties_cfg.get("update_schedule_time")

def update():
    subprocess.run("git pull ; python3.12 .".split(' '))

def check_update():
    needs_update = not "up to date" in subprocess.run("git remote update main ; git status | grep \"up to date\"".split(' '),encoding="utf-8", stdout=subprocess.PIPE).stdout
    
    if needs_update:
        print("\n\nPreparing update...")
        update()




async def UpdaterCycle():
    check_update()
    await sleep(60)