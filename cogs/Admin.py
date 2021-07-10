import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    async def cog_command_error(self, ctx, error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))
    
    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(aliases=['usc'], hidden = True)
    async def unloadSpecificCog(self,ctx,cog:str):
        try:
            self.bot.unload_extension("cogs." + cog)
            await ctx.send(f'Cog: {cog} unloaded!')
        except:
            await ctx.send("Cog nicht gefunden oder nicht geladen")

    @commands.command(aliases=['lsc'], hidden = True)
    async def loadSpecificCog(self,ctx,cog:str):
        try:
            self.bot.load_extension("cogs." + cog)
            await ctx.send(f'Cog: {cog} loaded!')
        except:
            await ctx.send("Cog nicht gefunden oder nicht geladen")

    @commands.command(hidden = True)
    async def echo(self,ctx,channel : discord.TextChannel, *message : str):
        print(message)
        await channel.send(" ".join(message[:]))
        await ctx.message.delete()






def setup(bot):
    bot.add_cog(Admin(bot))