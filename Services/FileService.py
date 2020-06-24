import os
from os.path import isdir, isfile, join, splitext
import random
from .Configurator import GetConfig, RndFileServiceConf


def GetDirs(Path):
    return __DiskObjWhere(Path, isdir)


def GetFiles(Path):    
    return __DiskObjWhere(Path, isfile)


def GetFilesToExtensions(Path, Extensions):
    return __DiskObjWhere(Path, lambda f: GetFileExtension(f) in Extensions)


def GetFileExtension(File):
    filename, file_extension = splitext(File)
    return file_extension


def __DiskObjWhere(Path, Predicate):
    res = []
    for o in os.listdir(Path):
        oJoin = join(Path, o)
        if Predicate(oJoin):
            res.append(oJoin)

    return res        


def GetRndFileUseConfProfileName(ProfileName):
    rndConf = GetConfig(RndFileServiceConf)
    return GetRndFile(rndConf["RootDirs"], rndConf["AllowedProfiles"][ProfileName], rndConf["BanDirs"])


def GetRndFile(Dirs, Extensions, BanDirs):
    random.seed(random.randint(1, 9999999999))

    dirDirs = { }
    dirHistory = []

    allowedExt = Extensions
    baseDirs = Dirs
    banDirs = set(BanDirs)

    for d in baseDirs:
        dirDirs[d] = list(set(GetDirs(d)) - banDirs)

    if len(dirDirs) > 0:
        curDir = list(dirDirs.keys())[random.randint(0, len(dirDirs) - 1)]
        childDirs = dirDirs[curDir]

        while len(dirDirs) > 0:
            if len(childDirs) > 0:
                goDown = random.randint(0, 100) <= 80
                if not goDown:
                    files = GetFilesToExtensions(curDir, allowedExt)
                    if len(files) > 0:
                        return files[random.randint(0, len(files) - 1)]

                curDir = childDirs.pop(random.randint(0, len(childDirs) - 1))
                childDirs = list(set(GetDirs(curDir)) - banDirs)
                dirDirs[curDir] = childDirs
                if len(childDirs) > 1:
                    dirHistory.append(curDir)
            else:
                files = GetFilesToExtensions(curDir, allowedExt)
                if len(files) > 0:
                    return files[random.randint(0, len(files) - 1)]
                else:
                    dirDirs.pop(curDir)
                    if len(dirHistory) > 0:
                        curDir = dirHistory.pop()
                        childDirs = dirDirs[curDir]
                    elif len(dirDirs) > 0:
                        rndIndex = random.randint(0, len(dirDirs) - 1)
                        curDir = list(dirDirs.keys())[rndIndex]
                        childDirs = dirDirs[curDir]  
    
    raise Exception('File not found!')