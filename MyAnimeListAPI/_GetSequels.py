from MyAnimeListAPI import GetAnimeList, GetAnimeInfo

animeList = [anime for anime in GetAnimeList.GetDetailed("mattyboyh2003") if anime["list_status"]["status"] == "completed" or anime["list_status"]["status"] == "watching"]
titleList = [anime["node"]["title"] for anime in GetAnimeList.GetFull("mattyboyh2003")]

l = []

for anime in animeList:
    animeLinks = anime["advanced_info"]["related_anime"]

    for animeLink in animeLinks:
        if animeLink["relation_type"] == "sequel" or animeLink["relation_type"] == "prequel":
            if animeLink["node"]["title"] not in titleList:
                
                linkInfo = GetAnimeInfo(animeLink["node"]["id"])

                if not linkInfo["media_type"] == "special":
                    l.append(linkInfo)


l.sort(key = lambda a : a["title"])
print("\n\n\n")
for i in l:
    print(f"{i['title']}: {i['media_type']}")
