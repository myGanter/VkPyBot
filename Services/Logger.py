import traceback
import sys
import os
import os.path
import datetime
from threading import Lock, Thread
from .Configurator import GetConfig, LoggerConf

__CurrentFile = None
__Error = False
__LogTextBoof = ""


def BeginLog():
    global __LogTextBoof, __Error
    __LogTextBoof = ""
    __Error = False


def Log(Msg):
    global __LogTextBoof
    now = datetime.datetime.now()
    now = "[" + str(now) + "] "  
    __LogTextBoof += now + Msg + "\n"
    conf = GetConfig(LoggerConf)
    if conf["DublicateToTerminal"]:
        print("[+] " + now + Msg)


def LogError(Msg):
    global __LogTextBoof, __Error
    __Error = True
    now = datetime.datetime.now()
    now = "[" + str(now) + "] "  
    __LogTextBoof += now + Msg + "\n"
    conf = GetConfig(LoggerConf)
    if conf["DublicateToTerminal"]:
        print("[-] " + now + Msg)


def EndLog():
    res = ""
    if __Error:
        res += "[-] "
    else:
        res += "[+] "

    now = datetime.datetime.now()
    now = str(now)  
    res += now + "\n"
    file = open(__GetLogFile(), "a", encoding="utf-8")
    file.write(res + __LogTextBoof + "\n\n\n")
    file.close()
    

def FormatException(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str


def __GetLogFile():
    global __CurrentFile    
    conf = GetConfig(LoggerConf)

    if __CurrentFile == None or (os.path.exists(__CurrentFile) and os.stat(__CurrentFile).st_size > conf["MaxFileSizeKB"] * 1024):
        now = datetime.datetime.now()
        now = now.strftime(" %d-%m-%Y %H.%M")       
        __CurrentFile = conf["LogsDir"] + "Log" + now + ".txt"

    return __CurrentFile
