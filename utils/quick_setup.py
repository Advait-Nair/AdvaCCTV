import re

# Quick setup tool
# Used to setup the config file on first run

def QuickSetup():
    print('\n'*11)
    print("AdvaCCTV Quick Setup\n")

    server_ip= input("Enter the server IP to use")
    server_port= input("Enter the server port to use")
    server_mode= "true" if "t" in input("Is this a server? (true/false)") else "false"

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