import aiohttp
import re
import json
import aiohttp
import loadconfig
import googleapiclient.discovery

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
YTDataJsonString = "YTData/{}/{}.json"
headers={'accept-language' :'en-US,en;q=0.9','Cache-Control': 'no-cache','User-Agent' : user_agent}


YTAPIKEY = loadconfig.__ytApiKey__
YT_CHANNEL_URL = "https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails&id={CHANNEL_ID}&key={API_KEY}"
YT_PLAYLISTS_URL = "https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={PLAYLIST_ID}&key={API_KEY}"

async def newestVideo(channel: str, guildID: str,playListID, session: aiohttp.ClientSession):
    async with session.get(YT_PLAYLISTS_URL.format(PLAYLIST_ID = playListID,API_KEY = YTAPIKEY ),headers=headers,cookies={'CONSENT': 'YES+42'}) as r:
        jsonData = await r.json()
    channelName = channel
    newestUrl = "https://youtube.com/watch?v=" + jsonData['items'][0]['contentDetails']['videoId']
    if isVideoNew(newestUrl,channelName, guildID ):
        await storeNewUrl(newestUrl,channelName, guildID)
        return newestUrl
    else:
        print("Kein neues video gefunden")
        return None
    
async def fillYTPlayListID(channelID : str, guildID : str, channelName : str, session : aiohttp.ClientSession):
    async with session.get(YT_CHANNEL_URL.format(CHANNEL_ID = channelID,API_KEY = YTAPIKEY),headers={'accept-language' :'en-US,en;q=0.9'},cookies={'CONSENT': 'YES+42'}) as r:
        jsonData = await r.json()
        playListID = jsonData['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        newDict = {"playlistID" : playListID}
        with open(YTDataJsonString.format(guildID,channelName), 'r+') as fileRead:
            data = json.load(fileRead)
            data.update(newDict)
            fileRead.seek(0)
            json.dump(data,fileRead, indent=4)
            fileRead.truncate()
            fileRead.close()

async def getPlayListIDFromJson(channelName : str, guildID : str):
    with open(YTDataJsonString.format(guildID,channelName),'r') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return data['playlistID']

async def storeNewUrl(newVideoUrl : str,channelName : str , guildID : str):
    newDict = {"newestVideoUrl":  newVideoUrl}
    with open(YTDataJsonString.format(guildID,channelName),'r+') as fileRead:
        data = json.load(fileRead)
        data.update(newDict)
        fileRead.seek(0)
        json.dump(data,fileRead, indent=4)
        fileRead.truncate()
        fileRead.close()


def isVideoNew(newestVideoUrl : str,channelName : str, guildID : str):
    with open(YTDataJsonString.format(guildID,channelName),'r+') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        try: 
            return not data['newestVideoUrl'] == newestVideoUrl
        except:
            return True
        
def getChannelUrlStrFromJson(channelName : str, guildID : str):
    with open(YTDataJsonString.format(guildID,channelName),'r') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return data['channelStr']

async def getChannelName(channelID : str, session : aiohttp.ClientSession):
    async with session.get(YT_CHANNEL_URL.format(CHANNEL_ID = channelID,API_KEY = YTAPIKEY),headers={'accept-language' :'en-US,en;q=0.9'},cookies={'CONSENT': 'YES+42'}) as r:
        json = await r.json()
        return json['items'][0]['snippet']['title']

def getDiscordChannelIDFromName(channelName :str, guildID : str):
    with open(YTDataJsonString.format(guildID,channelName),'r') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return data['DiscordChannel']

def getDiscordRoleFromName(channelName :str, guildID :str):
    with open(YTDataJsonString.format(guildID,channelName),'r') as fileRead:
        data = json.load(fileRead)
        fileRead.close()
        return data['DiscordRoleToMention']


