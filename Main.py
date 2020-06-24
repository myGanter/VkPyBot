from Services.VkApiService import SubscribeToTypeEvent, StartLongPool, LongPoolResponce
from Services.ComandService import ContainsComand, GetComand
from Services.Logger import Log, LogError
from vk_api.bot_longpoll import VkBotEventType


def Main():
    Log("Start app")    
    SubscribeToTypeEvent(VkBotEventType.MESSAGE_NEW, MessageNew)
    StartLongPool()


def MessageNew(Obj):
    comandName = Obj.SplitComand()
    Log("Comand: " + comandName)
    Log("FromId: " + str(Obj.GetFromId()))
    Log("PeerId: " + str(Obj.GetPeerId()))
    if ContainsComand(comandName):
        GetComand(comandName)(Obj)
    else:
        Log("Start * comand")
        GetComand("*")(Obj)


if __name__ == '__main__':
    Main()