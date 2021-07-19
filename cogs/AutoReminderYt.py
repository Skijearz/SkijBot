import asyncio
import discord
from discord.ext import commands, tasks
import logging
import os
import json
import ytAnnouncementLib
import loadconfig
import time

log = logging.getLogger("discord")
logging.basicConfig(level=os.environ.get('LOGLEVEL','INFO'))


YTDataJsonString = "YTData/{}/{}.json"

class AutoReminderYt(commands.Cog):
    

    def __init__(self,bot):
        self.bot = bot
        log.info("Cog AutoReminder loaded")
        self.REQUIRED_ROLE = loadconfig.__AnnouncementRole__
        if not os.path.exists("YTData/"):
            os.makedirs("YTData/")
        self.checkForNewVideoAndPostLoop.start()

        
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
    async def subYt(self,ctx,channel : discord.TextChannel, youtubeChannel:str,*role : str):


        channelName = ytAnnouncementLib.getChannelName(youtubeChannel)
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
        channelName = ytAnnouncementLib.getChannelName(youtubeChannel)
        if os.path.isfile(YTDataJsonString.format(ctx.guild.id,channelName)):
            os.remove(YTDataJsonString.format(ctx.guild.id,channelName))
            await ctx.send(f'**{channelName}** Deabonniert')
        else:
            await ctx.send(f'**{channelName}** ist nicht Abonniert')

    @commands.command()
    async def abosYt(self,ctx):
        embed = discord.Embed(title=f'YouTube Abos',type='rich',color=0x845EC2)
        embed.set_thumbnail(url=self.bot.AppInfo.icon_url)
        channel = os.listdir("YTData/"+ str(ctx.guild.id) + "/")
        valueString = ""
        for c in channel:
            valueString += c.split(".")[0]+"\n"
        embed.add_field(name="Derzeit Folge ich:",value=valueString)
        await ctx.send(embed=embed)

    @tasks.loop(seconds=60)
    async def checkForNewVideoAndPostLoop(self):
        start_time = time.time()
        guilds = os.listdir("YTData/")
        for g in guilds:
            channel = os.listdir("YTData/"+g + "/")
            for c in channel:
                channelName = c.split(".")[0]
                guildID = g
                log.info(f'Checking Youtube-Channel: {channelName}')
                channelUrl = ytAnnouncementLib.getChannelUrlStrFromJson(channelName,guildID)
                announcementURL = await ytAnnouncementLib.newestVideo(channelUrl,guildID,self.bot.session)
                if announcementURL is not None:
                    discordChannelid = ytAnnouncementLib.getDiscordChannelIDFromName(channelName,guildID)
                    role = ytAnnouncementLib.getDiscordRoleFromName(channelName,guildID)
                    channel = self.bot.get_channel(discordChannelid)
                    if channel is not None:
                        await channel.send(f'{role} Neues video von **{channelName}**:\n' + announcementURL)
                    else:
                        log.info("Channel nicht gefunden")
        log.info("Checking all YouTube-Channel took : --- %s seconds ---" % (time.time() - start_time))   

def setup(bot):
    bot.add_cog(AutoReminderYt(bot))
