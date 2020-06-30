from Services.VkApiService import LongPoolResponce, UploadPhotoOnStream, SendMsg, UploadVideoOnData, GetVideoLen, GetVideo
from .Logger import Log, LogError
from .FileService import GetFileExtension, GetRndFileUseConfProfileName, GetFileStream
from .SearchFacesApiService import UploadFile, Search
from .WitAiService import SpeechRecognitionFromMediaData, SpeechResponse
from .Configurator import GetConfig, RndFileServiceConf, SecureConf
import json
import requests 
import random

__Session = requests.Session()


def __GetComands(Obj):
    SendMsg("\n ".join(__Comands.keys()), Obj.GetPeerId())


def __AllOther(Obj):
    msgUri = Obj.GetAudioMsgUri()    
    if not msgUri == "":
        Log("Audio uri: " + msgUri)
        msgStream = requests.get(msgUri)
        speechResponseObj = SpeechRecognitionFromMediaData(msgStream.content)
        text = speechResponseObj.GetText()
        Log("Recognize text: " + text)
        if text == "":
            text = "..."
        SendMsg(text, Obj.GetPeerId())


def __GetPic(Obj):
    file = GetRndFileUseConfProfileName("Pic")
    Log(file)
    (fileStream, o) = GetFileStream(file)
    photo = UploadPhotoOnStream(fileStream)
    attachments = [ photo ]
    SendMsg("Держи", Obj.GetPeerId(), attachments)
    o.close()


def __GetVideo(Obj):
    args = Obj.SplitArgs()
    msg = "Держи"
    attachments = []

    Log("Args: " + str(args))
    if len(args) > 0:
        Log("Get random video from vk")
        conf = GetConfig(SecureConf)
        videoOvner = ""
        try:
            if args[0] == "group":
                videoOvner = -int(conf["GroupId"])
            else:            
                videoOvner = int(args[0])

            lens = GetVideoLen(videoOvner)
            Log("GetVideoLen: " + str(lens))
            if lens > 0:
                rndOffSet = random.randint(0, lens - 1)
                video = GetVideo(videoOvner, rndOffSet)
                Log("GetVideo: " + video)
                attachments.append(video)
            else:
                msg = "Videos not found"
                Log(msg)
        except:
            Log("Get random video from vk except")
            SendMsg("Args not valid", Obj.GetPeerId())
            raise            
    else:
        Log("Get random video from pc")
        file = GetRndFileUseConfProfileName("Video")
        Log(file)
        (fileStream, o) = GetFileStream(file)
        video = UploadVideoOnData(fileStream)        
        if "error" in video:
            msg = video["error"]
        else:
            attachments.append(video)

        o.close()

    SendMsg(msg, Obj.GetPeerId(), attachments)    


def __GetBidlos(Obj):
    uploadPhotoUri = Obj.GetUriFirstPhoto()
    Log("Upload photo: " + uploadPhotoUri)
    if not uploadPhotoUri == "":
        photoResponce = requests.get(uploadPhotoUri)
        photoInfo = UploadFile(photoResponce.content)
        photoResponce.close()
        faces = Search(photoInfo)

        if not faces == None:
            firstPics = faces.GetFirst3Pics()
            attachments = []
            for facePicUri in firstPics:
                facePic = __Session.get(facePicUri, stream=True)
                vkPhoto = UploadPhotoOnStream(facePic.raw)
                facePic.close()
                attachments.append(vkPhoto)

            SendMsg(faces.GetResponceString(), Obj.GetPeerId(), attachments)
        else:
            SendMsg("Not found", Obj.GetPeerId())
            

def ContainsComand(ComandName):
    return ComandName in __Comands


def GetComand(ComandName):
    return __Comands[ComandName]  


__Comands = {
    "get comands": __GetComands,
    "get pic": __GetPic,
    "get video": __GetVideo,
    "get bidlos": __GetBidlos,
    "*": __AllOther
} 