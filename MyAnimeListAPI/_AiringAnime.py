from MyAnimeListAPI import GetAnimeInfo, GetAnimeList, Date

# Get users full anime list
animeList = GetAnimeList.GetFull("mattyboyh2003")

# Filter out complete or dropped animes
animeList = [anime for anime in animeList if anime["list_status"]["status"] != "completed" and anime["list_status"]["status"] != "dropped"]


# Filter for the remaining anime
checkLambda = lambda a : GetAnimeInfo(a)["status"] == "currently_airing" or GetAnimeInfo(a)["status"] == "not_yet_aired"


# List of detailed anime info with all irrelevant anime filtered out
filteredList = [GetAnimeInfo(anime["node"]["id"]) for anime in animeList if checkLambda(anime["node"]["id"])]

# Add forced anime that aren't picked up in the innitial full list request
forcedAnime = [50709]
filteredList += [GetAnimeInfo(anime, refresh = True) for anime in forcedAnime if checkLambda(anime)]


animeDetails = {}

# Empty dictionary assigning each weekday a number
DAYSMAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}

# Create an empty list of 7 empty list to store the animes by day
animeByDays = [[] for _ in range(0,7)]

# Populate animeBroadcastTimes and titlesList
for anime in filteredList:
    if "broadcast" in anime.keys():
        animeDetails[anime["title"]] = {"broadcast" : anime["broadcast"], "status" : anime["status"]}

    elif "start_date" in anime.keys():
        if len(anime["start_date"].split("-")) == 3:
            startDate = anime["start_date"].split("-")

            #print(f"\n\n{startDate}\n\n")


# Calculate the broadcast days and times for each anime and store it based on broadcast day
for anime in list(animeDetails.keys()):
    broadcastDay = animeDetails[anime]["broadcast"]["day_of_the_week"]
    broadcastTime = animeDetails[anime]["broadcast"]["start_time"]

    date = Date(broadcastDay, broadcastTime)
    date.changeTimeZone("+1")

    animeByDays[DAYSMAP[date.GetDay()]].append([anime, date.GetTime(), animeDetails[anime]["status"]])


print(animeByDays)

# Output
print("\n\n\n")
counter = 0
for day in animeByDays:
    if day != []:
        print(f"{list(DAYSMAP.keys())[counter]}:")

        airingList = sorted([anime for anime in day if anime[2] == "currently_airing"], key = lambda a : a[1].split(":")[0] * 60 + a[1].split(":")[1])
        notAiringList = sorted([anime for anime in day if anime[2] == "not_yet_aired"], key = lambda a : a[1].split(":")[0] * 60 + a[1].split(":")[1])

        for anime in airingList:
            print(f"    Airing     │ {anime[0]} : {anime[1]}")
        if airingList and notAiringList:
            print("    ───────────┼───────────────────────────────")
        for anime in notAiringList:
            print(f"    Not Airing │ {anime[0]} : {anime[1]}")

    counter += 1
