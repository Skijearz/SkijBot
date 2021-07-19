import aiohttp
import re
import json
import aiohttp

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
YTDataJsonString = "YTData/{}/{}.json"
headers={'accept-language' :'en-US,en;q=0.9','Cache-Control': 'no-cache','User-Agent' : user_agent}


async def newestVideo(channel: str, guildID: str, session: aiohttp.ClientSession):
    async with session.get(channel+"/videos",headers=headers,cookies={'CONSENT': 'YES+42'}) as r:
        html = await r.text()
    channelName = await getChannelName(channel,session)
    newestUrl = "https://www.youtube.com/watch?v=" + re.search('(?<="videoId":").*?(?=")',html).group()
    if isVideoNew(newestUrl,channelName, guildID ):
        storeNewUrl(newestUrl,channelName, guildID)
        return newestUrl
    else:
        print("Kein neues video gefunden")
        return None
    


def storeNewUrl(newVideoUrl : str,channelName : str , guildID : str):
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

async def getChannelName(channelUrl : str, session : aiohttp.ClientSession):
    async with session.get(channelUrl,headers={'accept-language' :'en-US,en;q=0.9'},cookies={'CONSENT': 'YES+42'}) as r:
        html = await r.text()
    return re.search('(?<="name": ").*?(?=")',html).group()

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


