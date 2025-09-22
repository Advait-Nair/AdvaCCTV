
cd ~
git clone https://github.com/advait-nair/advacctv
cd advacctv

# Install dependencies

# Check for python3.12 and pip3.12
if ! command -v python3.12 &> /dev/null
then
    # install 3.12
    echo "Python 3.12 not found. Installing..."
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv
else
    echo "Python 3.12 found."
fi


# Ask use if they want to create a venv
read -p "Do you want to create a virtual environment? If not, pip flag --break-system-packages will install everything needed globally, and possibly break another Python project. (y/n): " create_venv
if [[ "$create_venv" == "y" || "$create_venv" == "Y" ]]; then
    python3.12 -m venv ./.venv
    source ./.venv/bin/activate
    echo "Virtual environment created and activated."
    pip3.12 install --upgrade pip
    pip3.12 install -r requirements.txt
else
    echo "Skipping virtual environment creation."
    echo "Installing dependencies globally. This will use --break-system-packages. You might need to use 'sudo' for the next command"
    sudo pip3.12 install -r requirements.txt --break-system-packages
fi

echo "

AdvaCCTV and it's dependencies have been installed!
__

Running Setup..."

python3.12 . setup
