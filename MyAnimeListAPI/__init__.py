import urllib3
import json
import time
import secrets

import MyAnimeListAPI.HTMLFuncs as _HTMLFuncs

################
# - Defaults - #
################

http = urllib3.PoolManager()

ROOTURL = "https://api.myanimelist.net/v2"
_DATAPATH = __file__.replace('\\__init__.py', '/Data')

with open(f"{_DATAPATH}/client.json", "r") as file:
    CLIENTID = json.loads(file.read())["CLIENTID"]
with open(f"{_DATAPATH}/me.json", "r") as file:
    me = json.loads(file.read())


###############
# - Classes - #
###############

class GetAnimeList:
    @staticmethod
    def base(username):
        endpoint = f"/users/{username}/animelist"
        animeList = []
        offset = 0
        while True:
            headers = {"X-MAL-CLIENT-ID" : CLIENTID, "Authorization" : f"Bearer {me['access_token']}"}
            fields = {"offset" : offset, "fields" : "list_status"}
            result = SendRequest(endpoint, fields, headers)

            animeList += result["data"]

            if "next" in result["paging"].keys():
                nextURL = result["paging"]["next"]
                qpos = nextURL.find("?")
                fpos = nextURL.find("fields")
                offset = int(nextURL[qpos+8:fpos-1])
            else:
                break
    
        return animeList
    
    @staticmethod
    def GetFull(username, refresh = False, save = True):
        if not refresh:
            cached, cachedData = CheckCache(username, "GetFull.json")

            if cached:
                return cachedData
        

        animeList = GetAnimeList.base(username)

        if save:
            saveData = {
                "Key" : username,
                "Data" : animeList
            }
            SaveResult(saveData, fileName = "GetFull.json", saveType = "Update")

        return animeList

    @staticmethod
    def GetWatching(username, refresh = False, save = True):
        if not refresh:
            cached, cachedData = CheckCache(username, "GetWatching.json")

            if cached:
                return cachedData

        animeList = GetAnimeList.base(username)

        animeList = [i for i in animeList if i["list_status"]["status"] == "watching"]

        if save:
            saveData = {
                "Key" : username,
                "Data" : animeList
            }
            SaveResult(saveData, fileName = "GetWatching.json", saveType = "Update")
        
        return animeList

    @staticmethod
    def GetDetailed(username, refresh = False, save = True):
        if not refresh:
            cached, cachedData = CheckCache(username, "GetDetailed.json")

            if cached:
                return cachedData

        animeList = GetAnimeList.base(username)
        detailedAnimeList = []

        for anime in animeList:
            print(f"Currently gathering info for: {anime['node']['title']}")

            detailedAnime = anime
            detailedAnime["advanced_info"] = GetAnimeInfo(anime["node"]["id"])
            detailedAnimeList.append(detailedAnime)

        if save:
            saveData = {
                "Key" : username,
                "Data" : animeList
            }
            SaveResult(saveData, fileName = "GetDetailed.json", saveType = "Update")
        
        return animeList

class Date:

    DaysMap = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
    }

    def __init__(self, dayStr : str, timeStr : str, timeZone = "+9"):
        splitTime = timeStr.split(":")

        self.day = dayStr
        self.hour = int(splitTime[0])
        self.min = int(splitTime[1])
        self.timeZone = timeZone
    
    def __repr__(self):
        return f"{self.day} {self.hour}:{self.min}"

    def changeTimeZone(self, timeZone):
        if timeZone == self.timeZone:
            return
        
        else:
            timeZoneShift = int(timeZone) - int(self.timeZone)

            if timeZoneShift < 0 and -timeZoneShift > self.hour:
                self.day = list(self.DaysMap.keys())[self.DaysMap[self.day]-1]
                self.hour = 24+(self.hour+timeZoneShift)
                self.timeZone = timeZone
            elif timeZoneShift > 0 and timeZoneShift >= 24 - self.hour:
                self.day = list(self.DaysMap.keys())[self.DaysMap[self.day]+1]
                self.hour = 24 - self.hour + timeZoneShift
                self.timeZone = timeZone
            else:
                self.hour += timeZoneShift
                self.timeZone = timeZone
    
    def GetTime(self):
        return f"{self.hour}:{self.min:02}"

    def GetDay(self):
        return str(self.day)


#################
# - Functions - #
#################

def CheckCache(key, file):
    with open(f"DataCache/{file}", "r") as jsonFile:
        fileContents = json.loads(jsonFile.read())
    
    if key in fileContents.keys():
        if fileContents[key]["TimeStamp"] >= time.time() - 86400:
            print(f"Recent data for '{key}' found in '{file}'")
            return True, fileContents[key]["Data"]
    
    return False, None

def SaveResult(data, fileName = "DefaultSave.json", saveType = "Replace"):
    
    print(f"Attempting to {saveType} {fileName}")
    
    if saveType == "Replace":
        with open(f"DataCache/{fileName}", "w") as jsonFile:
            jsonFile.write(json.dumps(data, sort_keys = True, indent = 4))
    
    elif saveType == "Append":
        with open(f"DataCache/{fileName}", "r") as jsonFile:
            fileContents = json.loads(jsonFile.read())
        fileContents.append(data)
        with open(f"DataCache/{fileName}", "w") as jsonFile:
            jsonFile.write(json.dumps(fileContents, sort_keys = True, indent = 4))
    
    elif saveType == "Update":
        # For the 'Update' save type to work the data input must be a dict structured as stated below:
        # {
        #   'Key' : str,
        #   'Data' : json format,
        #   'TimeStamp' (Optional) : int - Epoch time (If none given it is generated now)
        # }

        # Load current fileData
        with open(f"DataCache/{fileName}", "r") as jsonFile:
            fileContents = json.loads(jsonFile.read())

        # Check for required keys
        if "Key" in data.keys() and "Data" in data.keys():
            
            # Check for optional TimeStamp Key
            if "TimeStamp" in data.keys():
                timeStamp = data["TimeStamp"] # Save timestamp if given
            else:
                timeStamp = time.time()
            
            # Check if the new data is already present
            if data["Key"] in fileContents.keys(): # If the new data is already present, check to see if its newer
                if fileContents[data["Key"]]["TimeStamp"] < timeStamp: # If the present data is older overwrite it
                    fileContents[data["Key"]] = {"Data" : data["Data"], "TimeStamp" : timeStamp}
            else: # If the new data is not present, add it to the file
                fileContents[data["Key"]] = {"Data" : data["Data"], "TimeStamp" : timeStamp}
            
            with open(f"DataCache/{fileName}", "w") as jsonFile:
                jsonFile.write(json.dumps(fileContents, sort_keys = True, indent = 4))

        else:
            print(f"Unable to save data to {fileName}, invalid data format given for Update save type")

    else:
        print(f"Unable to save data to {fileName}, invalid saveType given")

def SendRequest(endpoint = "", fields = {}, headers = {}, URLOveride = None, resultType = "JSON"):

    print(f"Sending request to {endpoint}\n fields: {fields}\n headers: {headers}\n")

    if URLOveride:
        print(f"Sending request to {URLOveride}\n fields: {fields}\n")
        response = http.request("GET", f"{URLOveride}", headers = headers)
    else:
        print(f"Sending request to {endpoint}\n fields: {fields}\n")
        response = http.request("GET", f"{ROOTURL}{endpoint}", fields = fields, headers = headers)


    if response.status == 200:
        response = response.data.decode('utf-8')
        if resultType == "JSON":
            response = json.loads(response)

        return response
    else:
        print(response.status)
        #print(response.data)

        exit()

def GetAnimeInfo(id, refresh = False, save = True):
    if not refresh:
        cached, cachedData = CheckCache(str(id), "GetAnimeInfo.json")

        if cached:
            return cachedData

    endpoint = f"/anime/{id}"
    headers = {"X-MAL-CLIENT-ID" : CLIENTID, "Authorization" : f"Bearer {me['access_token']}"}
    fields = {"fields" : "id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics"}
    animeInfo = SendRequest(endpoint, fields, headers)

    if save:
        saveData = {
            "Key" : str(id),
            "Data" : animeInfo
        }
        SaveResult(saveData, fileName = "GetAnimeInfo.json", saveType = "Update")

    return animeInfo

def GetMangaInfo(id, refresh = False, save = True, returnFields = None):
    if not refresh:
        cached, cachedData = CheckCache(str(id), "GetMangaInfo.json")
        if cached:
            return cachedData

    endpoint = f"/manga/{id}"
    headers = {"X-MAL-CLIENT-ID" : CLIENTID, "Authorization" : f"Bearer {me['access_token']}"}
    if returnFields:
        fields = {"fields" : returnFields}
    else:
        fields = {"fields" : "id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics"}
    mangaInfo = SendRequest(endpoint, fields, headers)

    if save:
        saveData = {
            "Key" : str(id),
            "Data" : mangaInfo
        }
        SaveResult(saveData, fileName = "GetMangaInfo.json", saveType = "Update")

    return mangaInfo

def GetUserFavourites(user, refresh = False, save = True):
    if not refresh:
        cached, cachedData = CheckCache(str(user), "GetUserFavourites.json")
        if cached:
            return cachedData
    
    url = f"myanimelist.net/profile/{user}"
    headers = {}
    fields = {}
    userProfile = SendRequest("", fields, headers, URLOveride=url, resultType="HTML")


    results = {}
    lookFor = [
        "id=\"anime_favorites\"",
        "id=\"manga_favorites\"",
        "id=\"character_favorites\"",
        "id=\"company_favorites\"",
        "id=\"person_favorites\""
    ]

    for check in lookFor:
        # Look to see if the div with id 'check' is present
        pos = userProfile.find(check)
        if pos == -1:
            continue
        
        # cut newHTML down to just this div
        start = userProfile[:pos].rfind("<div")
        end = _HTMLFuncs.FindDivEnd(userProfile[start:]) + start

        newHTML = userProfile[start:end]


        # cut newHTML down to just the fav-slide-outer part of this div
        start = newHTML.find("class=\"fav-slide-outer\"")
        end = _HTMLFuncs.FindDivEnd(newHTML, start) + start

        newHTML = newHTML[start-4:end]


        # get all <a href=""> tags left in newHTML

        aTags = []

        start = 0
        while start != -1:
            start = newHTML.find("<a href=")
            end = newHTML[start+1:].find(">")

            aTags.append(newHTML[start:start+end])

            newHTML = newHTML[end+start+1:]
        
        aTags = aTags[:-1]
        
        # cut said <a> tags down to just the hrefs
        links = [tag.split("\"")[1] for tag in aTags]

        results[check.split("\"")[1].split("_")[0]] = links

    if save:
        saveData = {
            "Key" : str(user),
            "Data" : results
        }
        SaveResult(saveData, fileName = "GetUserFavourites.json", saveType = "Update")
    
    return results


######################
# - Auth Functions - #
######################

def GetCodeVerifier():
    token = secrets.token_urlsafe(100)
    return token[:128]

def GetAuthURL(codeVerifier, clientID):
    return f"https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={clientID}&code_challenge={codeVerifier}&state=IDKWhatImDoing"

def CompleteAuth(code, codeVerifier):
    url = "https://myanimelist.net/v1/oauth2/token"
    fields = {
        "client_id" : CLIENTID,
        "code" : code,
        "code_verifier" : codeVerifier,
        "grant_type" : "authorization_code"
    }

    response = http.request("POST", url, fields = fields)

    if response.status == 200:
        response = json.loads(response.data.decode('utf-8'))
    else:
        print(response.status)
        print(response.data)

        exit()

    return response


"""
All scopes for getting anime info:
    id,
    title,
    main_picture,
    alternative_titles,
    start_date,
    end_date,
    synopsis,
    mean,
    rank,
    popularity,
    num_list_users,
    num_scoring_users,
    nsfw,
    created_at,
    updated_at,
    media_type,
    status,
    genres,
    my_list_status,
    num_episodes,
    start_season,
    broadcast,
    source,
    average_episode_duration,
    rating,pictures,
    background,
    related_anime,
    related_manga,
    recommendations,
    studios,
    statistics
"""
