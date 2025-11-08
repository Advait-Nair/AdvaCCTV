import os
from utils.arguments import is_flag_present_arg
VERBOSE = (os.path.exists('.dev') or is_flag_present_arg('v')) and not is_flag_present_arg('-mute','-m')