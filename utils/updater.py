# Update the whole program on a commit.

from utils.config import properties_cfg
from asyncio import sleep
import subprocess
from utils.log import log


check_rate = properties_cfg.get("update_check_rate")
from utils.config import CONFIG_PATH
def update():
    # Save toml file

    # toml = ""
    # with open(CONFIG_PATH, 'r') as f:
    #     toml = f.read()
    #     f.close()

    subprocess.run("git pull".split(' '))

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
        update()
        log("Update complete! The server will auto-restart.")
        print('\n'*10)




async def UpdaterCycle():
    while True:
        check_update()
        await sleep(float(check_rate))