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
REQUIRED_ROLE = "Chef"
YTDataJsonString = "YTData/{}/{}.json"

class AutoReminder(commands.Cog):
    

    def __init__(self,bot):
        self.bot = bot
        log.info("Cog AutoReminder loaded")

        self.ytAnnouncementLoop = asyncio.ensure_future(self.checkForNewVideoAndPostLoop())
        
    async def cog_command_error(self, ctx, error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    async def cog_check(self,ctx):
        member = ctx.author
        role = discord.utils.get(ctx.guild.roles, name=REQUIRED_ROLE)
        if role in member.roles:
            return True
        else:
            return False

    @commands.command()
    async def subYt(self,ctx,channel : discord.TextChannel, youtubeChannel:str,*role : str):
        channelName = recentVideoLib.getChannelName(youtubeChannel)
        roles = "".join(role[:])
        if os.path.exists(YTDataJsonString.format(ctx.guild.id,channelName)):
            await ctx.send(f'**{channelName}** Bereits Aboniert')
        else:
            if not os.path.exists("YTData/" + str(ctx.guild.id)):
                os.makedirs("YTData/" + str(ctx.guild.id))

            with open(YTDataJsonString.format(ctx.guild.id,channelName),'w') as file:
                tempDict = {"channelStr" : youtubeChannel,"DiscordChannel" : channel.id,"DiscordRoleToMention" : roles}
                tempJson = json.dumps(tempDict, indent=4)
                file.write(tempJson)
                file.close()
            await ctx.send(f'**{channelName}** Abonniert')
    
    @commands.command()
    async def unSubYt(self,ctx,youtubeChannel:str):
        channelName = recentVideoLib.getChannelName(youtubeChannel)
        if os.path.isfile(YTDataJsonString.format(ctx.guild.id,channelName)):
            os.remove(YTDataJsonString.format(ctx.guild.id,channelName))
            await ctx.send(f'**{channelName}** Deabonniert')
        else:
            await ctx.send(f'**{channelName}** ist nicht Abonniert')

    @commands.command()
    async def abos(self,ctx):
        embed = discord.Embed(title=f'YouTube Abos',type='rich',color=0x845EC2)
        embed.set_thumbnail(url=self.bot.AppInfo.icon_url)
        channel = os.listdir("YTData/"+ str(ctx.guild.id) + "/")
        valueString = ""
        for c in channel:
            valueString += c.split(".")[0]+"\n"
        embed.add_field(name="Derzeit Folge ich:",value=valueString)
        await ctx.send(embed=embed)


    async def checkForNewVideoAndPostLoop(self):

        
        while True:
            guilds = os.listdir("YTData/")
            
            for g in guilds:
                channel = os.listdir("YTData/"+g + "/")
                for c in channel:
                    channelName = c.split(".")[0]
                    guildID = g
                    channelUrl = recentVideoLib.getChannelUrlStrFromJson(channelName,guildID)
                    announcementURL = recentVideoLib.newestVideo(channelUrl,guildID)
                    if announcementURL is not None:
                        discordChannelid = recentVideoLib.getDiscordChannelIDFromName(channelName,guildID)
                        role = recentVideoLib.getDiscordRoleFromName(channelName,guildID)
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
