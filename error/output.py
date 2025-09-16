from enum import Enum



class CodeType(Enum):
    Error = "E"
    Info = "C"
    Warn = "W"
    Verbose = "V"


def output(title:str=None, msg:str=None, code:int=-1, ctype:CodeType=CodeType.Info, e:Exception=None):
    print(f"""
    
    {ctype.value}{code} :: {title} :: {msg}

    """)

    if e == None: return

    print(f"""    === BEGIN ERROR DETAIL ===
    
    {e}

    ===  END  ERROR DETAIL ===
    
    """)

