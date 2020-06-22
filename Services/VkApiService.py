from .Configurator import GetConfig, SecureConf
from .FileService import GetFileExtension, GetRndFileUseConf
import json
import requests
import vk_api
from vk_api import VkUpload
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

__VkSession = vk_api.VkApi(token=GetConfig(SecureConf)["ApiKey"])
__Upload = VkUpload(__VkSession)
__Vk = __VkSession.get_api()
__LongPool = VkBotLongPoll(__VkSession, GetConfig(SecureConf)["GroupId"])
__TypeEvents = {}


class LongPoolResponce:

    def __init__(self, Obj):
        self.Obj = Obj


    def GetMessage(self):
        return self.Obj["message"]["text"]  
        

    def SplitComand(self):
        msg = self.GetMessage()
        if len(msg) > 0:
            if msg[:1] == "[":
                words = msg.split()
                if len(words) > 1:
                    return " ".join(words[1:])
        
        return msg


    def GetPeerId(self):
        return self.Obj["message"]["peer_id"]


    def GetUriFirstPhoto(self):
        if len(self.Obj["message"]["attachments"]) > 0:
            first = self.Obj["message"]["attachments"][0]
            if "photo" in first and len(first["photo"]["sizes"]) > 0:
                lastSize = first["photo"]["sizes"][len(first["photo"]["sizes"]) - 1]
                return lastSize["url"]

        return ""


def SubscribeToTypeEvent(TypeEvent, Clbk):
    if not TypeEvent in __TypeEvents:
        __TypeEvents[TypeEvent] = []

    __TypeEvents[TypeEvent].append(Clbk)


def StartLongPool():
    for event in __LongPool.listen():
        evType = event.type
        if evType in __TypeEvents:
            obj = LongPoolResponce(__GetDictObj(event.obj))
            for clbk in __TypeEvents[evType]:
                clbk(obj)


def UploadPhotoOnStream(PhotoData):
    photo = __Upload.photo_messages(photos=PhotoData)[0]
    return 'photo{}_{}'.format(photo['owner_id'], photo['id'])


def SendMsg(Msg, PeerId, Attachment = []):
    __Vk.messages.send(
        message=Msg,
        attachment=','.join(Attachment),
        random_id=get_random_id(),
        peer_id=PeerId
    )


def __GetDictObj(Obj):
    return json.loads(json.dumps(Obj))