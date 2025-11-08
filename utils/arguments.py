import sys
import traceback
argvj=' '.join(sys.argv)


flags_overview_str = ''

def process_flag(flag:str, case_sensitive=False) -> bool:
    if case_sensitive:
        return flag.strip() in sys.argv
    else:
        return flag.strip().lower() in sys.argv or flag.strip() in sys.argv
    


def is_flag_present_arg(*flag:list[str], case_sensitive=False):
    global flags_overview_str
    # if type(flag) == str:
    #     return process_flag(flag, case_sensitive=case_sensitive)
    # else:
    for f in flag:
        if process_flag(f, case_sensitive=case_sensitive):
            flags_overview_str += f"+ {f.replace('-','').strip().lower()}\n"
            return True

def get_cli_value_arg(flag:str, converter=str, default=None, case_sensitive=False):
    global flags_overview_str
    value = default
    proc_flag = process_flag(flag, case_sensitive=case_sensitive)
    if proc_flag:
        try:
            value = converter(argvj.split(flag)[1].strip().split(' ')[0].strip())
        except Exception as e:
            print(e) if is_flag_present_arg('-v') else None
            value = default
    flags_overview_str += f"{flag.replace('-','').strip().lower()} -> {value}\n"
    return value
