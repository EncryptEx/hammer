from discord.member import Member
from get_enviroment import COMMAND_PREFIX, TOKEN
import discord
from discord import Embed

from discord.ext import commands
from discord.ext.commands.core import command

bot = commands.Bot(command_prefix="/")

debug = True

@commands.command()
async def hello(ctx):
    await ctx.send("Hammer is back!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'**[ERROR 404]** Please pass in all requirements :hammer_pick:. ```{error}```\nDo  {COMMAND_PREFIX}help command for more help')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("[**ERROR 403]** You dont the correct permission to do that :hammer:")

@commands.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    if member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself")
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been banned from {ctx.guild.name} for {reason}"

    if(not debug):
        await member.ban(reason = reason)
    descr= f"The user {member} has been banned for {reason}"
    embed = Embed(title=F"{member} has been banned! :hammer_pick:", description=descr)
    embed.set_image(url="https://i.imgflip.com/19zat3.jpg")
    embed.set_footer(text=f"Hammer | {ctx.message.author}", icon_url="https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670")
    embed.set_thumbnail(url=member.avatar_url)
    await ctx.send(embed=embed)
    await member.send(message)

@commands.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx, member : discord.Member, *, reason = None):
    if member == ctx.message.author:
        await ctx.channel.send("You cannot kick yourself")
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been kicked from {ctx.guild.name} for {reason}"
    if(not debug):
        await member.kick(reason = reason)
    descr= f"The user {member} has been kicked for {reason}"
    embed = Embed(title=F"{member} has been kicked! :hammer_pick:", description=descr)
    embed.set_footer(text=f"Hammer | {ctx.message.author}", icon_url="https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670")
    embed.set_thumbnail(url=member.avatar_url)
    # # embed.image = member.image
    await ctx.send(embed=embed)
    await member.send(message)
    
@commands.command()
@commands.has_permissions(kick_members = True)
async def warn(ctx, member : discord.Member, *, reason = None):
    if member == ctx.message.author:
        await ctx.channel.send("You cannot warn yourself :(")
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been warned for {reason}"

    descr= f"The user {member} has been warned for {reason}"
    embed = Embed(title=F"{member} has been warned! :hammer_pick:", description=descr)
    embed.set_footer(text=f"Hammer | {ctx.message.author}", icon_url="https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670")
    embed.set_thumbnail(url=member.avatar_url)

    await ctx.send(embed=embed)
    await member.send(message)


bot.add_command(hello)
bot.add_command(kick)
bot.add_command(ban)
bot.add_command(warn)
bot.run(TOKEN)
