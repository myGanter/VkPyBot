import requests 
import json

__UserAgent = type('',(object,),{
    "Name": "user-agent",
    "Value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
})()

__ImgContent = type('',(object,),{
    "Name": "content-type",
    "Value": "image/png"
})()

__TextContent = type('',(object,),{
    "Name": "content-type",
    "Value": "text/plain;charset=UTF-8"
})()


class SearchResponce:

    def __init__(self, Obj):
        self.Obj = Obj


    def GetFacesCount(self):
        return self.Obj["faces_found"]


    def GetResponceString(self):
        if self.GetFacesCount() > 0 and "faces" in self.Obj:
            bidlos = []
            for face in self.Obj["faces"]:
                boofStr = "["
                boofStr += face[10] + "%] "
                boofStr += face[1]
                bidlos.append(boofStr)
        
            return "\n".join(bidlos)

        return "Not found"


    def GetFirst3Pics(self):
        pics = []
        if self.GetFacesCount() > 0 and "faces" in self.Obj:
            ind = 0
            for face in self.Obj["faces"]:
                if ind > 2:
                    break
                pics.append("https:" + face[2])
                ind += 1

        return pics


def UploadFile(File):
    res = requests.post("https://search4faces.com/upload.php", headers={__UserAgent.Name: __UserAgent.Value, __ImgContent.Name: __ImgContent.Value}, data=File)
    return json.loads(res.text)


def Search(PersInfo):
    if not "boundings" in PersInfo:
        return None

    data = {
        "query":"vkok",
        "filename":PersInfo["url"],
        "boundings":PersInfo["boundings"][0]
    }
    data = json.dumps(data)
    response = requests.post("https://search4faces.com/detect.php", headers={__UserAgent.Name: __UserAgent.Value, __TextContent.Name: __TextContent.Value}, data=data)
    response = json.loads(response.text)

    return SearchResponce(response)