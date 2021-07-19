import logging
from discord.ext.commands.core import is_owner
import pkg_resources
import os
import discord
from discord import activity
from discord.ext import commands
import loadconfig
import aiohttp
import twitchAnnouncementLib


__version__ = '0.1.4'
description = '''Tooki ba waba! '''


log = logging.getLogger("discord")
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=os.environ.get('LOGLEVEL','INFO'),datefmt='%Y-%m-%d %H:%M:%S')

class SkijBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=loadconfig.__prefix__,description=description,intents=intents)

        self.session = aiohttp.ClientSession()


    async def on_message(self,message):
        if message.author.bot:
            return
        if isinstance(message.channel,discord.DMChannel) and not await self.is_owner(message.author):
            await message.author.send('Der Bot unterstützt keine DMs, bitte nutze den Server dafür!')
            return
        await self.process_commands(message)

    async def on_ready(self):
        log.info('=============')
        log.info('Bot Started')
        log.info(f'Bot-Version: {__version__}')
        log.info(f'Bot-Name: {self.user.name}')
        log.info(f'Bot-ID {self.user.id}')
        self.AppInfo = await self.application_info()
        log.info(f'Owner: {self.AppInfo.owner}')
        log.info(f'Discord.Py Version: {pkg_resources.get_distribution("discord.py").version}')
        log.info('=============')
        game = discord.Game("Ohanna heißt Familie")
        await self.change_presence(status=discord.Status.online,activity=game)
        self.botVersion = __version__

        self.load_extension("cogs.Info")
        self.load_extension("cogs.Crash")
        self.load_extension("cogs.Admin")
        self.load_extension("cogs.AutoReminderYt")
        self.load_extension("cogs.AutoReminderTwitch")

        if not twitchAnnouncementLib.isTokenValid():
            await twitchAnnouncementLib.createAuthToken(self.session)
    
    async def close(self):
        await super().close()
        await self.session.close()
    

if __name__ == '__main__':
    bot = SkijBot()
    bot.run(loadconfig.__token__)