import discord
from discord.ext import commands
from getRecentCrashes import getRecentCrashes

class Crash(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def cog_command_error(self,ctx,error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    @commands.command(aliases=['ct','rc'])
    async def recentCrashes(self,ctx,recentCrashesAmount = None):
        if recentCrashesAmount is not None:
            recentCrashesList = getRecentCrashes(recentCrashesAmount)
            embed = discord.Embed(title=f':chart_with_upwards_trend: WTFSkins: die {recentCrashesAmount} letzten Crashpoints',type='rich',color=0x845EC2)
            valueString = ''
            for x in recentCrashesList:
                if(x > 7.0):
                    valueString += "```fix\n" + str(x) + "```"
                else:
                    valueString += "```\n" + str(x) + "\n```"
                    
            embed.add_field(name="Sortiert von neu zu alt:" ,value=valueString)
            await ctx.send(embed = embed)
        else:
            await ctx.send("Keine Anzahl angegeben!")


def setup(bot):
    bot.add_cog(Crash(bot))