import requests
import loadconfig
import json
import time
import os
API_URL = 'https://api.twitch.tv/helix/streams?user_login={}'
API_URL_PROFILE_IMAGE = 'https://api.twitch.tv/helix/users?login={}'
OAUTH_URL = 'https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials'

APICHANNELID = loadconfig.__twitchAPIChannelID__
APISECRET = loadconfig.__twitchAPIKey__

TwitchDataJsonString = "TwitchData/{}/{}.json"
TwitchConfigFile = "config/twitchAPIConfig.json"


def checkForLiveChannel(TwitchChannel : str, guildID : str, session):
    
    print(TwitchChannel)
    APIAUTHTOKEN = ''

    
    with open(TwitchConfigFile, 'r') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        APIAUTHTOKEN = data['API_TOKEN']

    start_time = time.time()
    twitchResponse = session.get(API_URL.format(TwitchChannel), headers={'Client-ID': APICHANNELID, 'Authorization' : 'Bearer ' + APIAUTHTOKEN})
    twitchResponseImage = session.get(API_URL_PROFILE_IMAGE.format(TwitchChannel), headers={'Client-ID': APICHANNELID, 'Authorization' : 'Bearer ' + APIAUTHTOKEN}).text
    print(twitchResponse.elapsed.total_seconds())
    print("--- %s seconds REQ---" % (time.time() - start_time))
    jsonData = json.loads(twitchResponse.text)
    if not len(jsonData['data']) == 0:
        lastStreamed = jsonData['data'][0]['started_at']

    
    jsonImage = json.loads(twitchResponseImage)


    if not 'data' in jsonData or len(jsonData['data']) == 0 or getLastStreamed(guildID,TwitchChannel) == lastStreamed:
        

        return None
    else:
        setLastStreamed(guildID,TwitchChannel,lastStreamed)
        print("--- %s seconds REQ---" % (time.time() - start_time))
        return {'user_name' : jsonData['data'][0]['user_name'],'game_name' : jsonData['data'][0]['game_name'],'title' : jsonData['data'][0]['title'],'viewer_count':jsonData['data'][0]['viewer_count'],'thumbnail_url' : jsonData['data'][0]['thumbnail_url'],'profile_image_url' : jsonImage['data'][0]['profile_image_url']}

def createAuthToken():
    oauthResponse = requests.post(OAUTH_URL.format(APICHANNELID,APISECRET)).text
    jsonData = json.loads(oauthResponse)
    APITOKEN = jsonData['access_token']
    EXPIRES_IN = jsonData['expires_in']
    EXPIRES = time.time() + EXPIRES_IN -10
    TOKENTYPE = jsonData['token_type']

    newDict = {"API_TOKEN" : APITOKEN,"EXPIRES" : EXPIRES, "TOKEN_TYPE" : TOKENTYPE}
    with open(TwitchConfigFile,'r+') as fileRead:
        data = json.load(fileRead)
        data.update(newDict)
        fileRead.seek(0)
        json.dump(data,fileRead, indent=4)
        fileRead.truncate()
        fileRead.close()

def isTokenValid():
    if not os.path.isfile(TwitchConfigFile):
        return False

    with open(TwitchConfigFile, 'r') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return not data['EXPIRES'] <= time.time()
         
def getDiscordChannelFromName(guildID : str,channelName : str):
    with open(TwitchDataJsonString.format(guildID,channelName)) as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return data['DiscordChannel']

def getDiscordRoleFromName(guildID: str,channelName :str):
    with open(TwitchDataJsonString.format(guildID,channelName)) as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return data['DiscordRoleToMention']

def setLastStreamed(guildID,channelName,value : str):
        newDict = {"LastStreamed" : value}
        with open(TwitchDataJsonString.format(guildID,channelName),'r+') as fileRead:
            data = json.load(fileRead)
            data.update(newDict)
            fileRead.seek(0)
            json.dump(data,fileRead, indent=4)
            fileRead.truncate()
            fileRead.close()

def getLastStreamed(guildID,channelName):
    with open(TwitchDataJsonString.format(guildID,channelName),'r') as fileRead:
            data = json.load(fileRead)
            fileRead.close()
            return data['LastStreamed']




if __name__ == "__main__":
    checkForLiveChannel("revedtv",745495001622118501)


    
