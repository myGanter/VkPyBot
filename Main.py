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
    Log(comandName)
    if ContainsComand(comandName):
        GetComand(comandName)(Obj)  


if __name__ == '__main__':
    Main()