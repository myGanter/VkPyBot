import os
import io
from os.path import isdir, isfile, join, splitext
import random
from .Configurator import GetConfig, RndFileServiceConf
from ftplib import FTP
from .Logger import Log, LogError

class FtpClient:

    def __init__(self, Ftp):
        self.Ftp = Ftp
        self.CurDir = None


    def Cd(self, Path):
        if self.CurDir == Path:
            return
        
        self.CurDir = Path

        Log("FtpClient cd: " + Path)
        self.Ftp.cwd(Path.encode('cp1251').decode('ISO-8859-1'))

        res = [] 
        self.Ftp.dir(lambda line: res.append( [ i for i in line.encode('ISO-8859-1').decode('cp1251').split(" ") if not i == "" ] ))
        self.Dirs = []
        self.Files = []

        for i in res:
            if i[2] == "<DIR>":
                self.Dirs.append(" ".join(i[3:]))
            else:
                self.Files.append(" ".join(i[3:]))


    def GetFiles(self):
        return self.Files


    def GetDirs(self):
        return self.Dirs


__FtpClients = {}


def GetFileStream(Path):
    if __IsFtp(Path) == True:
        host = __GetFtpHost(Path)        
        realPath = __GetFtpRealPath(Path)
        ftp = FTP(host)
        ftp.login()
        memStream = io.BytesIO()
        ftp.retrbinary('RETR ' + realPath.encode('cp1251').decode('ISO-8859-1'), memStream.write)
        memStream.seek(0)
        return (memStream, memStream)
    else:
        f = open(Path, 'rb')
        return (f.raw, f)


def GetDirs(Path):
    if __IsFtp(Path) == True:
        ftp = __GetFtpClient(__GetFtpHost(Path))
        realPath = __GetFtpRealPath(Path)
        ftp.Cd(realPath)
        return [Path + i + "\\" for i in ftp.GetDirs()]
    else:
        return __DiskObjWhere(Path, isdir)


def GetFiles(Path):
    if __IsFtp(Path) == True:
        ftp = __GetFtpClient(__GetFtpHost(Path))
        realPath = __GetFtpRealPath(Path)
        ftp.Cd(realPath)
        return [Path + i for i in ftp.GetFiles()]
    else:
        return __DiskObjWhere(Path, isfile)


def GetFilesToExtensions(Path, Extensions):
    if __IsFtp(Path) == True:
        ftp = __GetFtpClient(__GetFtpHost(Path))
        realPath = __GetFtpRealPath(Path)
        ftp.Cd(realPath)
        return [Path + i for i in [ f for f in ftp.GetFiles() if GetFileExtension(f) in Extensions]]
    else:
        return __DiskObjWhere(Path, lambda f: GetFileExtension(f) in Extensions)


def GetFileExtension(File):
    if __IsFtp(File) == True:
        File = __GetFtpRealPath(File)        
    
    filename, file_extension = splitext(File)
    return file_extension


def __CloseFtpHendlers():
    global __FtpClients
    for k in __FtpClients:
        __FtpClients[k].Ftp.quit()

    __FtpClients = {}


def __GetFtpClient(Host):
    if Host in __FtpClients:
        return __FtpClients[Host]
    else:
        ftp = FtpClient(FTP(Host, timeout=10))
        __FtpClients[Host] = ftp
        ftp.Ftp.login()
        return ftp


def __IsFtp(Path):
    splPath = Path.split(" ")
    return len(splPath) > 0 and splPath[0] == "ftp"


def __GetFtpHost(Path):
    splPath = Path.split(" ")
    return splPath[1]


def __GetFtpRealPath(Path):
    splPath = Path.split(" ")
    return " ".join(splPath[2:])


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
        if len(childDirs) > 1:
            dirHistory.append(curDir)

        while len(dirDirs) > 0:
            if len(childDirs) > 0:
                goDown = random.randint(0, 100) <= 80
                if not goDown:
                    files = GetFilesToExtensions(curDir, allowedExt)
                    if len(files) > 0:
                        __CloseFtpHendlers()
                        return files[random.randint(0, len(files) - 1)]

                curDir = childDirs.pop(random.randint(0, len(childDirs) - 1))
                childDirs = list(set(GetDirs(curDir)) - banDirs)
                dirDirs[curDir] = childDirs
                if len(childDirs) > 1:
                    dirHistory.append(curDir)
            else:
                files = GetFilesToExtensions(curDir, allowedExt)
                if len(files) > 0:
                    __CloseFtpHendlers()
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
    
    __CloseFtpHendlers()
    raise Exception('File not found!')