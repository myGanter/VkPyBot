from Services.VkApiService import LongPoolResponce, UploadPhotoOnStream, SendMsg
from .Logger import Log, LogError
from .FileService import GetFileExtension, GetRndFileUseConf
from .SearchFacesApiService import UploadFile, Search
import json
import requests 

__Session = requests.Session()


def __GetComands(Obj):
    SendMsg("\n ".join(__Comands.keys()), Obj.GetPeerId())


def __GetPic(Obj):
    file = GetRndFileUseConf()
    Log(file)
    fileStream = open(file, 'rb')
    photo = UploadPhotoOnStream(fileStream.raw)
    attachments = [ photo ]
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
    "get bidlos": __GetBidlos
} 