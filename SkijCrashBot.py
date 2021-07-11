import logging
from discord.ext.commands.core import is_nsfw, is_owner
import pkg_resources
import os
import discord
from discord import activity
from discord.ext import commands
import loadconfig
from getRecentCrashes import getRecentCrashes


__version__ = '0.1.2'
description = '''Pablo... er ist Schiffbrüchig '''


log = logging.getLogger("SkijBot")
logging.basicConfig(level=os.environ.get('LOGLEVEL','INFO'))

class SkijBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=loadconfig.__prefix__,description=description,intents=intents)


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
        game = discord.Game("Wir sind Schiffbrüchig!")
        await self.change_presence(status=discord.Status.online,activity=game)
        self.botVersion = __version__

        self.load_extension("cogs.Info")
        self.load_extension("cogs.Crash")
        self.load_extension("cogs.Admin")
        self.load_extension("cogs.AutoReminder")


        



if __name__ == '__main__':
    bot = SkijBot()
    bot.run(loadconfig.__token__)