from Services.VkApiService import LongPoolResponce, UploadPhotoOnStream, SendMsg, UploadVideoOnData
from .Logger import Log, LogError
from .FileService import GetFileExtension, GetRndFileUseConfProfileName
from .SearchFacesApiService import UploadFile, Search
from .WitAiService import SpeechRecognitionFromMediaData, SpeechResponse
from .Configurator import GetConfig, RndFileServiceConf
import json
import requests 

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
    fileStream = open(file, 'rb')
    photo = UploadPhotoOnStream(fileStream.raw)
    attachments = [ photo ]
    SendMsg("Держи", Obj.GetPeerId(), attachments)
    fileStream.close()


def __GetVideo(Obj):
    file = GetRndFileUseConfProfileName("Video")
    Log(file)
    fileStream = open(file, 'rb')
    video = UploadVideoOnData(fileStream.raw)
    attachments = [ video ]
    SendMsg("Держи", Obj.GetPeerId(), attachments)
    fileStream.close()


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