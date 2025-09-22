from pathlib import Path
import re
from utils.systemctl_restarter import Restarter

# Quick setup tool
# Used to setup the config file on first run

def _QuickSetup():
    print('\n'*11)
    print("AdvaCCTV Quick Setup\n")

    # Append acctv to .bashrc if not already present
    with open(f"{str(Path.home())}/.bashrc", "r") as f:
        bashrc = f.read()
        if "alias acctv=" not in bashrc:
            with open(f"{str(Path.home())}/.bashrc", "a") as fa:
                fa.write('\n# AdvaCCTV Alias\nalias acctv="cd ~/AdvaCCTV && python3.12 ."\n')
                fa.close()

    input("Bashrc alias has been created. Run shortcut is 'acctv'. Press Enter to continue with parameter modification, or ^C to abort...")
    
    
    server_ip= input("Enter the server IP to use : ")
    server_port= input("Enter the server port to use : ")
    server_mode= "true" if "t" in input("Is this a server? (true/false) : ") else "false"

    with open("config.toml", "r") as f:
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
        print("Please fix the issue and run 'python3.12 . setup' again. Internal error? Log an issue on GitHub at Advait-Nair/AdvaCCTV.")
        exit(1)