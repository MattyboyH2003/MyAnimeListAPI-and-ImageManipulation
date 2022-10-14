from MyAnimeListAPI import GetAnimeList

animeList = GetAnimeList.GetDetailed("IceCreamScene", save = True)
animeList = [anime for anime in animeList if anime["list_status"]["status"] != "plan_to_watch"]

animeByScore = [[] for _ in range(0, 11)]
genreByScore = [{} for _ in range(0, 12)]

for anime in animeList:
    animeByScore[anime["list_status"]["score"]].append(anime)

for counter, animes in enumerate(animeByScore):
    for anime in animes:
        if "genres" in list(anime["advanced_info"].keys()):
            for genre in anime["advanced_info"]["genres"]:
                if genre["name"] in list(genreByScore[counter].keys()):
                    genreByScore[counter][genre["name"]] += 1
                else:
                    genreByScore[counter][genre["name"]] = 1

                if genre["name"] in list(genreByScore[11].keys()):
                    genreByScore[11][genre["name"]] += 1
                else:
                    genreByScore[11][genre["name"]] = 1

        else:
            print(f"No genres found for {anime['node']['title']}")

genreByScoreList = [[key, genreByScore[11][key]] for key in list(genreByScore[11].keys())]

genreByScoreList.sort(key = lambda a : a[1], reverse = True)

for genre in genreByScoreList:
    print(f"{genre[0]}: {genre[1]}")
