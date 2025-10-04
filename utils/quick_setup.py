from pathlib import Path
import re
from utils.systemctl_restarter import Restarter
from utils.config import pyv
import os

# Quick setup tool
# Used to setup the config file on first run

def _QuickSetup():
    print('\n'*11)
    print("AdvaCCTV Quick Setup\n")

    pyv = input("Enter the python version to use (default 3.12) : ").strip() or "3.12"
    with open("config_base.toml", "r") as f:
        contents = f.read()
        
        # Replace pyv with quotes
        contents = re.sub(r'pyv\s*=\s*"[^"]*"', f'pyv="{pyv}"', contents)
        
        # Write the updated content back
        with open("config_base.toml", "w") as write_f:
            write_f.write(contents)
            write_f.close()

        f.close()

    # Append acctv to .bashrc if not already present
    with open(f"{str(Path.home())}/.bashrc", "r") as f:
        bashrc = f.read()
        # Check if the alias already exists in bashrc
        if 'alias acctv=' in bashrc:
            # Remove the existing alias
            bashrc = re.sub(r'\n# AdvaCCTV Alias\nalias acctv=.*\n', '\n', bashrc)
            # Write the cleaned bashrc back
            with open(f"{str(Path.home())}/.bashrc", "w") as fw:
                fw.write(bashrc)
                fw.close()
        
        def w(fa):
            venvstr = "source ./.venv/bin/activate && " if os.path.exists('./.venv') else ''
            fa.write(f'\n# AdvaCCTV Alias\nalias acctv="cd ~/AdvaCCTV && {venvstr} python{pyv} . $@"\n')
            fa.close()
            
        bpath = f"{str(Path.home())}/."
        with open(bpath + 'bashrc', "a") as fa: w(fa)
        if os.path.exists(bpath + 'zshrc'):
            with open(bpath + 'zshrc', "a") as fa: w(fa)

        f.close()

    input(".bashrc alias has been created. Run shortcut is 'acctv'.\nNote that changes will require a terminal reload.\n\nPress Enter to continue with parameter modification, or ^C to abort: ")
    
    
    server_ip= input("\nEnter the server IP to use when in daemon mode   : ")
    server_port= input("Enter the server port to use for both modes      : ")
    server_mode= "true" if "t" in input("Is this a server by default? (true/false)        : ") else "false"

    with open("config_base.toml", "r") as f:
        contents = f.read()
        
        # Replace server_ip with quotes
        contents = re.sub(r'server_ip\s*=\s*"[^"]*"', f'server_ip="{server_ip}"', contents)
        
        # Replace server_port without quotes (as integer)
        contents = re.sub(r'server_port\s*=\s*[^\n]*', f'server_port={server_port}', contents)
        
        # Replace server_mode without quotes (as boolean)
        contents = re.sub(r'server_mode\s*=\s*[^\n]*', f'server_mode={server_mode.lower()}', contents)

        
        
        # Write the updated content back
        with open("config.toml", "w") as write_f:
            write_f.write(contents)
            write_f.close()

        f.close()

    
    autostart_req = True if 'y' in input ("Do you want to auto-setup systemd service? (Y/N) : ").lower() else False
    if autostart_req:
        Restarter()

def QuickSetup():
    try:
        _QuickSetup()
        print("\n\nSetup complete! Please restart the terminal or run 'source ~/.bashrc' to apply the alias.")
        print("You can now run the program using the 'acctv' command from any directory.")
    except KeyboardInterrupt:
        print("\n\nSetup aborted!\n")
        exit(1)
    except Exception as e:
        print(f"\n\nSetup failed: {e}")
        print(f"Please fix the issue and run 'python{pyv} . setup' again. Internal error? Log an issue on GitHub at Advait-Nair/AdvaCCTV.")
        exit(1)