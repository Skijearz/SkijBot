import logging
import os
import discord
from discord import activity
from discord.ext import commands
import loadconfig
from getRecentCrashes import getRecentCrashes


__version__ = '0.1'
description = '''Skijearzs WTF-Skins CrashPoint Bot'''


log = logging.getLogger("SkijBot")
logging.basicConfig(level=os.environ.get('LOGLEVEL','INFO'))

class SkijBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=loadconfig.__prefix__,description=description,intents=intents)


    async def on_ready(self):
        log.info('=============')
        log.info('Bot Started')
        log.info(f'Bot-Name: {self.user.name}')
        log.info(f'Bot-ID {self.user.id}')
        self.AppInfo = await self.application_info()
        log.info(f'Owner: {self.AppInfo.owner}')
        log.info('=============')
        game = discord.Game("Danny hat n klein Schniedel")
        await self.change_presence(status=discord.Status.online,activity=game)



        @self.command(name='recentCrashes',aliases=['ct'])
        async def recentCrashes(ctx,recentCrashesAmount):
            recentCrashesList = getRecentCrashes(recentCrashesAmount)
            embed = discord.Embed(title=f':chart_with_upwards_trend: WTFSkins Letzten {recentCrashesAmount} Crashpoints',type='rich',color=0x845EC2)
            valueString = ''
            for x in recentCrashesList:
                valueString += str(x) + '\n'  
                
            embed.add_field(name="Sortiert von neu zu alt:" ,value=valueString)
            await ctx.send(embed = embed)



if __name__ == '__main__':
    bot = SkijBot()
    bot.run(loadconfig.__token__)