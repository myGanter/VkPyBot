from .Configurator import GetConfig, SecureConf
from .Logger import BeginLog, EndLog, Log, LogError, FormatException
import json
import requests
import vk_api
from vk_api import VkUpload
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

__VkSession = vk_api.VkApi(token=GetConfig(SecureConf)["ApiKey"])
__VkUser = vk_api.VkApi(login=GetConfig(SecureConf)["Login"], password=GetConfig(SecureConf)["Password"], scope=140422623)
__VkUser.auth()
__Upload = VkUpload(__VkSession)
__Vk = __VkSession.get_api()
__LongPool = VkBotLongPoll(__VkSession, GetConfig(SecureConf)["GroupId"])
__TypeEvents = {}


class LongPoolResponce:

    def __init__(self, Obj):
        self.Obj = Obj


    def GetAudioMsgUri(self):
        if len(self.Obj["message"]["attachments"]) > 0:
            first = self.Obj["message"]["attachments"][0]
            if "audio_message" in first:
                lastSize = first["audio_message"]
                return lastSize["link_mp3"]

        return ""


    def GetMessage(self):
        return self.Obj["message"]["text"]  
        

    def SplitComand(self):
        msg = self.GetMessage()
        if len(msg) > 0 and msg != "?":
            msg = msg.split("?")[0]

            if msg[:1] == "[":
                words = msg.split()
                if len(words) > 1:
                    return " ".join(words[1:])
        
        return msg


    def SplitArgs(self):
        msg = self.GetMessage()
        res = []
        if "?" in msg:
            args = msg.split("?")[1].split(" ")
            for arg in args:
                if not "" == arg:
                    res.append(arg)

        return res


    def GetPeerId(self):
        return self.Obj["message"]["peer_id"]


    def GetFromId(self):
        return self.Obj["message"]["from_id"]


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
        try:
            BeginLog()
            evType = event.type
            Log(str(evType))
            if evType in __TypeEvents:
                Log(str(event.obj))
                obj = LongPoolResponce(__GetDictObj(event.obj))
                for clbk in __TypeEvents[evType]:
                    clbk(obj)
        except Exception as exc:
            textEx = FormatException(exc)
            LogError(textEx)
        finally:
            EndLog()


def GetVideoLen(OvnerId):
    response = __VkUser.method("video.get", { "owner_id":OvnerId, "count":0, "offset":0 })
    return response["count"]


def GetVideo(OvnerId, Offset):
    response = __VkUser.method("video.get", { "owner_id":OvnerId, "count":1, "offset":Offset })
    video = response["items"][0]
    return 'video{}_{}'.format(video['owner_id'], video['id'])


def UploadVideoOnData(VideoData):
    recVS = __VkUser.method("video.save", { "is_private": True })
    recV = requests.post(recVS["upload_url"], files={ "video_file": VideoData }).json()
    if "error" in recV:
        Log("UploadVideoError: " + recV["error"])
        return recV

    return 'video{}_{}'.format(recV['owner_id'], recV['video_id'])


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