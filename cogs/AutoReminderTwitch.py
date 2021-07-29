import discord
from discord.ext import commands
from discord.ext import tasks
import loadconfig
import os
import json
import asyncio
import twitchAnnouncementLib
import logging
import time
import traceback
import random as r


log = logging.getLogger("discord")
logging.basicConfig(level=os.environ.get('LOGLEVEL','INFO'))

TwitchDataJsonString = "TwitchData/{}/{}.json"

class AutoReminderTwitch(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.REQUIRED_ROLE = loadconfig.__AnnouncementRole__
        if not os.path.exists("TwitchData/"):
            os.makedirs("TwitchData/")
        self.checkForLiveChannelAndNotify.start()

    async def cog_command_error(self, ctx, error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    async def cog_check(self,ctx):
        member = ctx.author
        if member.guild_permissions.administrator:
            return True
        else:
            await ctx.send(":no_entry: Du benötigst Administrator rechte für diesen Befehl!")
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
                tempDict = {"channelStr" : twitchChannel,"DiscordChannel" : Channel.id,"DiscordRoleToMention" : roles,"LastStreamed" : 0}
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
            
    @tasks.loop(seconds=120)
    async def checkForLiveChannelAndNotify(self):
        try:
            start_time = time.time()
            guilds = os.listdir("TwitchData/")
            for g in guilds:
                channel = os.listdir("TwitchData/"+g+"/") 
                tasks = []  
                for c in channel:
                    channelName = c.split(".")[0]
                    guildID = g
                    task = asyncio.ensure_future(self.asyncWorkerLiveChannelCheck(guildID,channelName))
                    tasks.append(task)
                await asyncio.gather(*tasks,return_exceptions=True)
        except:
            log.info(traceback.print_exc())
        log.info("Checking all Twitch-Channel took : --- %s seconds ---" % (time.time() - start_time))      

    async def asyncWorkerLiveChannelCheck(self,guildID,channelName):
        twitchResponse = await twitchAnnouncementLib.checkForLiveChannel(channelName,guildID,self.bot.session)
        if twitchResponse is not None:
            channelID = twitchAnnouncementLib.getDiscordChannelFromName(guildID,channelName)
            roles = twitchAnnouncementLib.getDiscordRoleFromName(guildID,channelName)
            channel = self.bot.get_channel(channelID)
            embed = discord.Embed(title=twitchResponse['title'],url=f"https://twitch.tv/{channelName}",type='rich',color=0x845EC2)
            embed.set_author(name=twitchResponse["user_name"])
            embed.set_thumbnail(url = twitchResponse['profile_image_url'])
            embed.add_field(name="Game", value=twitchResponse['game_name'], inline=True)
            embed.add_field(name="Viewers", value=twitchResponse['viewer_count'], inline = True)
            embed.set_image(url=twitchResponse['thumbnail_url'].format(width = 320, height = 180)+str(r.randint(1000,9999)))
            await channel.send(f'{roles} {twitchResponse["user_name"]} ist nun Live!!', embed=embed)


def setup(bot):
    bot.add_cog(AutoReminderTwitch(bot))