import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    

    async def cog_command_error(self,ctx,error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    @commands.command(aliases=['stats','status'])
    async def info(self,ctx):
        botOwner = self.bot.AppInfo.owner
        amountGuilds = len(self.bot.guilds)
        amountOfMembersInGuild = len(list(self.bot.get_all_members()))
        embed = discord.Embed(title=f'{self.bot.user.name} Stats',type='rich',color=0x845EC2)
        embed.set_thumbnail(url=self.bot.AppInfo.icon_url)
        embed.add_field(name="Owner",value=botOwner, inline=False)
        embed.add_field(name="Anzahl Server", value=amountGuilds, inline=True)
        embed.add_field(name="#Member: ", value=amountOfMembersInGuild,inline=True)
        embed.add_field(name="Bot-Version", value=self.bot.botVersion,inline=True)
        embed.add_field(name="Discord.py-Version",value=discord.__version__,inline=True)
        embed.add_field(name="Letzter YT-Checker Ping", value= '%.2f' %self.bot.ytCheckerPing + " Sekunden", inline = True)
        embed.add_field(name="Letzter Twitch-Checker Ping", value= '%.2f' %self.bot.twCheckerPing + " Sekunden", inline = True)  
        embed.set_footer(text="Experiment 6-2-6")
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Info(bot))