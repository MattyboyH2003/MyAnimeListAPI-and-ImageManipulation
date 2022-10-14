import urllib3
import os
from MyAnimeListAPI import GetAnimeInfo, GetMangaInfo
from MyAnimeListAPI.Errors import Error

_HTTP = urllib3.PoolManager()

def DownloadImage(id, type):
    if type.lower() == "manga":
        info = GetMangaInfo(id)
    elif type.lower() == "anime":
        info = GetAnimeInfo(id)
    else:
        raise Error("Invalid type for image request")
    
    savedImages = [f for f in os.listdir(f"DataCache\\Images\\{type}\\Large") if os.path.isfile(os.path.join(f"DataCache\\Images\\type\\Large", f))]
    if f"{id}.jpg" not in savedImages:
        headers = {}
        fields = {}
        response = _HTTP.request("GET", info["main_picture"]["large"], fields = fields, headers = headers)

        if response.status == 200:
            response = response.data
            with open(f"DataCache\\Images\\{type}\\Large\\{id}.jpg", "wb") as img:
                img.write(response)
        else:
            print(response.status)
            print(response.data)
    else:
        print(f"Image for {type} {id} already found")
    
    return f"DataCache\\Images\\{type}\\Large\\{id}.jpg"

def DownloadBulk(l):
    return [DownloadImage(item["id"], item["type"]) for item in l]
