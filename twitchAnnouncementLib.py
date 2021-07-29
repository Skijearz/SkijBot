import loadconfig
import json
import time
import os
import aiohttp

API_URL = 'https://api.twitch.tv/helix/streams?user_login={}'
API_URL_PROFILE_IMAGE = 'https://api.twitch.tv/helix/users?login={}'
OAUTH_URL = 'https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials'

APICHANNELID = loadconfig.__twitchAPIChannelID__
APISECRET = loadconfig.__twitchAPIKey__

TwitchDataJsonString = "TwitchData/{}/{}.json"
TwitchConfigFile = "config/twitchAPIConfig.json"



async def checkForLiveChannel(TwitchChannel : str, guildID : str, session: aiohttp.ClientSession):

    APIAUTHTOKEN = ''

    with open(TwitchConfigFile, 'r') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        APIAUTHTOKEN = data['API_TOKEN']

    async with session.get(API_URL.format(TwitchChannel),headers={'Client-ID': APICHANNELID, 'Authorization' : 'Bearer ' + APIAUTHTOKEN}) as r:
        twitchResponseJsonData = await r.json()
        if r.status == 401:
            await createAuthToken()
            return None

    async with session.get(API_URL_PROFILE_IMAGE.format(TwitchChannel), headers={'Client-ID': APICHANNELID, 'Authorization' : 'Bearer ' + APIAUTHTOKEN}) as r:
        twitchResponseImageJson = await r.json()

    if await isJsonPopulated(twitchResponseJsonData):
        lastStreamed = twitchResponseJsonData['data'][0]['started_at']
        if await getLastStreamed(guildID,TwitchChannel) != lastStreamed:
            await setLastStreamed(guildID,TwitchChannel,lastStreamed)
            return {'user_name' : twitchResponseJsonData['data'][0]['user_name'],'game_name' : twitchResponseJsonData['data'][0]['game_name'],'title' : twitchResponseJsonData['data'][0]['title'],'viewer_count':twitchResponseJsonData['data'][0]['viewer_count'],'thumbnail_url' : twitchResponseJsonData['data'][0]['thumbnail_url'],'profile_image_url' : twitchResponseImageJson['data'][0]['profile_image_url']}
        else:
            return None
    else:
        return None
        
async def createAuthToken(session : aiohttp.ClientSession):
    async with session.post(OAUTH_URL.format(APICHANNELID,APISECRET)) as r:
        jsonData = await r.json()
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

async def isTokenValid():
    if not os.path.isfile(TwitchConfigFile):
        return False

    with open(TwitchConfigFile, 'r') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return not data['EXPIRES'] <= time.time()
         
async def getDiscordChannelFromName(guildID : str,channelName : str):
    with open(TwitchDataJsonString.format(guildID,channelName)) as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return data['DiscordChannel']

async def getDiscordRoleFromName(guildID: str,channelName :str):
    with open(TwitchDataJsonString.format(guildID,channelName)) as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return data['DiscordRoleToMention']

async def setLastStreamed(guildID,channelName,value : str):
        newDict = {"LastStreamed" : value}
        with open(TwitchDataJsonString.format(guildID,channelName),'r+') as fileRead:
            data = json.load(fileRead)
            data.update(newDict)
            fileRead.seek(0)
            json.dump(data,fileRead, indent=4)
            fileRead.truncate()
            fileRead.close()

async def getLastStreamed(guildID,channelName):
    with open(TwitchDataJsonString.format(guildID,channelName),'r') as fileRead:
            data = json.load(fileRead)
            fileRead.close()
            return data['LastStreamed']

async def isJsonPopulated(json):
    return 'data' in json and len(json['data']) != 0

if __name__ == "__main__":
    checkForLiveChannel("revedtv",745495001622118501)


    
