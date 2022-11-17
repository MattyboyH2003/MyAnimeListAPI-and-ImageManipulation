from MyAnimeListAPI import GetCodeVerifier, GetAuthURL, CompleteAuth
import json

with open("MyAnimeListAPI/Data/client.json", "r") as file:
    CLIENTID = json.loads(file.read())["CLIENTID"]
    
with open("MyAnimeListAPI/Data/me.json", "r") as file:
    me = json.loads(file.read())

AUTHFILE = "MyAnimeListAPI/Data/me.json"

me["codeVerifier"] = GetCodeVerifier()

print("Please click the link below and return the code given")
print(GetAuthURL(me["codeVerifier"], CLIENTID))

code = input()

response = CompleteAuth(code, me["codeVerifier"])
print(response)

with open(AUTHFILE, "w") as authFile:
    authFile = authFile.write(json.dumps(response))
