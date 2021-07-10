import asyncio
import discord
from discord.ext import commands
import logging
import os
import json
import recentVideoLib 

log = logging.getLogger("SkijBot")
logging.basicConfig(level=os.environ.get('LOGLEVEL','INFO'))

##TODO: AUTOREMINDER Funktion auf Discord Guilds aufteilen somit können selbe channel auch in unterschiedlichen servern abonniert werden.

class AutoReminder(commands.Cog):
    REQUIRED_ROLE = "Youtube"

    def __init__(self,bot):
        self.bot = bot
        log.info("Cog AutoReminder loaded")

        self.ytAnnouncementLoop = asyncio.ensure_future(self.checkForNewVideoAndPostLoop())
        
    async def cog_command_error(self, ctx, error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    async def cog_check(self,ctx):
        member = ctx.author
        role = discord.utils.get(ctx.guild.roles, name="Chef")
        if role in member.roles:
            return True
        else:
            return False

    @commands.command()
    async def subYt(self,ctx,channel : discord.TextChannel, youtubeChannel:str,*role : str):
        channelName = recentVideoLib.getChannelName(youtubeChannel)
        roles = "".join(role[:])
        if os.path.isfile("YTData/"+channelName +".json"):
            await ctx.send(f'**{channelName}** Bereits Aboniert')
        else:
            with open("YTData/"+channelName +".json",'w') as file:
                tempDict = {"channelStr" : youtubeChannel,"DiscordChannel" : channel.id,"DiscordRoleToMention" : roles}
                tempJson = json.dumps(tempDict, indent=4)
                file.write(tempJson)
                file.close()
            await ctx.send(f'**{channelName}** Abonniert')
    
    @commands.command()
    async def unSubYt(self,ctx,youtubeChannel:str):
        channelName = recentVideoLib.getChannelName(youtubeChannel)
        if os.path.isfile("YTData/"+channelName +".json"):
            os.remove("YTData/"+channelName +".json")
            await ctx.send(f'**{channelName}** Deabonniert')
        else:
            await ctx.send(f'**{channelName}** ist nicht Abonniert')

    @commands.command()
    async def abos(self,ctx):
        embed = discord.Embed(title=f'YouTube Abos',type='rich',color=0x845EC2)
        embed.set_thumbnail(url=self.bot.AppInfo.icon_url)
        channel = os.listdir("YTData/")
        valueString = ""
        for c in channel:
            valueString += c.split(".")[0]+"\n"
        embed.add_field(name="Derzeit Folge ich:",value=valueString)
        await ctx.send(embed=embed)


    async def checkForNewVideoAndPostLoop(self):

        
        while True:
            channel = os.listdir("YTData/")
            
            for c in channel:
                channelName = c.split(".")[0]
                channelUrl = recentVideoLib.getChannelUrlStrFromJson(channelName)
                announcementURL = recentVideoLib.newestVideo(channelUrl)
                if announcementURL is not None:
                    discordChannelid = recentVideoLib.getDiscordChannelIDFromName(channelName)
                    role = recentVideoLib.getDiscordRoleFromName(channelName)
                    channel = self.bot.get_channel(discordChannelid)
                    if channel is not None:
                        await channel.send(f'{role} Neues video von **{channelName}**:\n' + announcementURL)
                    else:
                        log.info("Channel nicht gefunden")
            await asyncio.sleep(1*60)

                    
                


    @commands.Cog.listener()
    async def on_ready(self):
        print("test")


def setup(bot):
    bot.add_cog(AutoReminder(bot))
