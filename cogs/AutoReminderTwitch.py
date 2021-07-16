import discord
from discord.ext import commands
import loadconfig
import os
import json
import asyncio
import twitchAnnouncementLib
import logging
import time
import requests

log = logging.getLogger("SkijBot")
logging.basicConfig(level=os.environ.get('LOGLEVEL','INFO'))

TwitchDataJsonString = "TwitchData/{}/{}.json"

class AutoReminderTwitch(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.REQUIRED_ROLE = loadconfig.__AnnouncementRole__
        if  not twitchAnnouncementLib.isTokenValid():
            twitchAnnouncementLib.createAuthToken()
        session = requests.Session()
        self.twitchAnnouncementLoop = asyncio.ensure_future(self.checkForLiveChannelAndNotify(session))


    async def cog_command_error(self, ctx, error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    async def cog_check(self,ctx):
        member = ctx.author
        role = discord.utils.get(ctx.guild.roles, name=self.REQUIRED_ROLE)
        if role in member.roles:
            return True
        else:
            return False

    @commands.command()
    async def subTwitch(self,ctx,Channel : discord.TextChannel, twitchChannel : str , *role : str ):

        
        twitchChannelName = twitchChannel.split("/")[-1]
        roles = "".join(role[:])

        if os.path.exists(TwitchDataJsonString.format(ctx.guild.id,twitchChannel)):
             await ctx.send(f'**{twitchChannelName}** Bereits Aboniert')
        else:
            if not os.path.exists("TwitchData/"+ str(ctx.guild.id)):
                os.makedirs("TwitchData/"+ str(ctx.guild.id))

            with open(TwitchDataJsonString.format(ctx.guild.id,twitchChannelName),'w') as file:
                tempDict = {"channelStr" : twitchChannel,"DiscordChannel" : Channel.id,"DiscordRoleToMention" : roles,"ShouldBeMentioned" : True,"LastStreamed" : 0}
                tempJson = json.dumps(tempDict, indent=4)
                file.write(tempJson)
                file.close()
            await ctx.send(f'**{twitchChannelName}** Abonniert')


    @commands.command()
    async def unSubTwitch(self,ctx,twitchChannel:str):
        twitchChannelName = twitchChannel.split("/")[-1]
        if os.path.isfile(TwitchDataJsonString.format(ctx.guild.id,twitchChannelName)):
            os.remove(TwitchDataJsonString.format(ctx.guild.id,twitchChannelName))
            await ctx.send(f'**{twitchChannelName}** Deabonniert')
        else:
            await ctx.send(f'**{twitchChannelName}** ist nicht Abonniert')

    async def checkForLiveChannelAndNotify(self,session):
        if not os.path.exists("TwitchData/"):
            os.makedirs("TwitchData/")

        while(True):
            guilds = os.listdir("TwitchData/")
            for g in guilds:
                channel = os.listdir("TwitchData/"+g+"/")
                for c in channel:
                    start_time = time.time()
                    channelName = c.split(".")[0]
                    guildID = g
                    twitchResponse = twitchAnnouncementLib.checkForLiveChannel(channelName,guildID,session)
                    print("--- %s seconds ---" % (time.time() - start_time))
                    if twitchResponse is not None:
                        channelID = twitchAnnouncementLib.getDiscordChannelFromName(guildID,channelName)
                        roles = twitchAnnouncementLib.getDiscordRoleFromName(guildID,channelName)
                        channel = self.bot.get_channel(channelID)
                        embed = discord.Embed(title=twitchResponse['title'],url=f"https://twitch.tv/{channelName}",type='rich',color=0x845EC2)
                        embed.set_author(name=twitchResponse["user_name"])
                        embed.set_thumbnail(url = twitchResponse['profile_image_url'])
                        embed.add_field(name="Game", value=twitchResponse['game_name'], inline=True)
                        embed.add_field(name="Viewers", value=twitchResponse['viewer_count'], inline = True)
                        embed.set_image(url=twitchResponse['thumbnail_url'].format(width = 320, height = 180))
                        await channel.send(f'{roles} {twitchResponse["user_name"]} ist nun Live!!', embed=embed)
                    

            await asyncio.sleep(1*60)
                    




def setup(bot):
    bot.add_cog(AutoReminderTwitch(bot))