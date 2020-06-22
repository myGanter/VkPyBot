import json
import os
import os.path
from threading import Lock, Thread

RndFileServiceConf = "RndFileServiceConf"
SecureConf = "SecureConf"
LoggerConf = "LoggerConf"

__RelativeConfigPath = "Configs/"

__ConfigCache = { }
__FileLastEditCache = { }

__Locker = Lock()


def GetConfig(Name):   
    filePath = __CombineName(Name)
    __Locker.acquire()
    try:
        if Name in __ConfigCache:
            __UpdateConf(filePath, Name)
        else:
            __AddConf(filePath, Name)

        result = __ConfigCache[Name]
    finally:
        __Locker.release()
    return result


def __UpdateConf(Path, Name):
    if os.path.exists(Path):
        changeTime = os.path.getmtime(Path)
        if Name in __FileLastEditCache and __FileLastEditCache[Name] != changeTime:
            confFile = open(Path, 'r', encoding="utf-8")
            try:
                data = json.load(confFile)
                __ConfigCache[Name] = data
                __FileLastEditCache[Name] = changeTime
            finally:
                confFile.close()
            

def __AddConf(Path, Name):
    if os.path.exists(Path):
        changeTime = os.path.getmtime(Path)
        confFile = open(Path, 'r', encoding="utf-8")
        try:
            data = json.load(confFile)
            __ConfigCache[Name] = data
            __FileLastEditCache[Name] = changeTime
        finally:
            confFile.close()        
    else:
        __ConfigCache[Name] = { }


def __CombineName(Name):
    return __RelativeConfigPath + Name + ".json"