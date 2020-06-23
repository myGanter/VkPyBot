import requests 
import json
from .Configurator import GetConfig, SecureConf

class SpeechResponse:

    def __init__(self, Obj):
        self.Obj = Obj

    
    def GetText(self):
        if "text" in self.Obj:
            return self.Obj["text"]
        
        return ""


def SpeechRecognitionFromMediaData(Data):
    config = GetConfig(SecureConf)
    headers = {
        "Authorization": "Bearer " + config["WitAiApiKey"],
        "Accept": "audio/x-mpeg-3",
        "Content-Type": "audio/mpeg3"
    }
    response = requests.post("https://api.wit.ai/speech", headers=headers, data=Data)
    obj = json.loads(response.text)
    return SpeechResponse(obj)