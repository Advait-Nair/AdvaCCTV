"""
AdvaCCTV Auto-Start Setup Script
This script creates a systemd service to automatically start the AdvaCCTV application on boot.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, check=True, shell=False):
    """Run a shell command and return the result."""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, 
                                  capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def create_startup_script():
    """Create the startup script that will be called by systemd."""
    script_path = Path.home() / "start_advacctv.sh"
    advacctv_path = Path.home() / "AdvaCCTV"
    
    script_content = f"""#!/bin/bash

# Set up pyenv environment
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"

# Change to the application directory
cd {advacctv_path}

# Run the Python application
python3.12 .
"""
    
    print(f"Creating startup script at {script_path}")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    print("✓ Startup script created and made executable")
    
    return script_path

def create_systemd_service(script_path):
    """Create the systemd service file."""
    service_content = f"""[Unit]
Description=AdvaCCTV Daemon
After=network.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=5
User={os.getenv('USER', 'pi')}
Group={os.getenv('USER', 'pi')}
WorkingDirectory={Path.home() / 'AdvaCCTV'}
ExecStart={script_path}
StandardOutput=journal
StandardError=journal
SyslogIdentifier=advacctv

[Install]
WantedBy=multi-user.target
"""
    
    service_path = "/etc/systemd/system/advacctv.service"
    temp_service_path = "/tmp/advacctv.service"
    
    print(f"Creating systemd service file")
    with open(temp_service_path, 'w') as f:
        f.write(service_content)
    
    # Move the service file to the system directory (requires sudo)
    run_command(['sudo', 'cp', temp_service_path, service_path])
    run_command(['sudo', 'chown', 'root:root', service_path])
    run_command(['sudo', 'chmod', '644', service_path])
    
    # Clean up temp file
    os.remove(temp_service_path)
    print("✓ Systemd service file created")

def setup_systemd_service():
    """Enable and start the systemd service."""
    print("Reloading systemd daemon...")
    run_command(['sudo', 'systemctl', 'daemon-reload'])
    
    print("Enabling advacctv service...")
    run_command(['sudo', 'systemctl', 'enable', 'advacctv.service'])
    
    print("Starting advacctv service...")
    run_command(['sudo', 'systemctl', 'start', 'advacctv.service'])
    
    print("✓ Service enabled and started")

def check_service_status():
    """Check if the service is running properly."""
    print("\nChecking service status...")
    result = run_command(['sudo', 'systemctl', 'is-active', 'advacctv.service'], check=False)
    
    if result.returncode == 0 and result.stdout.strip() == 'active':
        print("✓ Service is running!")
    else:
        print("⚠ Service may not be running properly. Check with: sudo systemctl status advacctv.service")
    
    # Show brief status
    run_command(['sudo', 'systemctl', 'status', 'advacctv.service', '--no-pager', '-l'], check=False)

def Restarter():
    """Main setup function."""
    print("=== AdvaCCTV Auto-Start Setup ===\n")
    
    # Check if running as root (we shouldn't be)
    if os.getuid() == 0:
        print("❌ Please don't run this script as root. Run as normal user (the script will use sudo when needed).")
        sys.exit(1)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    expected_dir = Path.home() / "AdvaCCTV"
    
    if current_dir != expected_dir:
        print(f"⚠ Current directory: {current_dir}")
        print(f"⚠ Expected directory: {expected_dir}")
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("Please run this script from the AdvaCCTV directory")
            sys.exit(1)
    
    try:
        # Step 1: Create startup script
        script_path = create_startup_script()
        
        # Step 2: Create systemd service
        create_systemd_service(script_path)
        
        # Step 3: Enable and start service
        setup_systemd_service()
        
        # Step 4: Check status
        check_service_status()
        
        print("\n=== Setup Complete! ===")
        print("\nAdvaCCTV will now:")
        print("• Start automatically on boot")
        print("• Restart automatically if it crashes")
        print("• Run in the background as a system service")
        
        print("\nUseful commands:")
        print("• Check status: sudo systemctl status advacctv.service")
        print("• View logs: sudo journalctl -u advacctv.service -f")
        print("• Stop service: sudo systemctl stop advacctv.service")
        print("• Start service: sudo systemctl start advacctv.service")
        print("• Restart service: sudo systemctl restart advacctv.service")
        
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

