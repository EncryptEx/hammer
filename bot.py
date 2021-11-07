import discord
from get_enviroment import COMMAND_PREFIX, OWNER, TOKEN
from discord import Embed
from aioconsole import aexec
from discord.ext import commands
from discord.ext.commands.core import command
from time import time
import sys
import os

import datetime

bot = commands.Bot(command_prefix="/")

debug = False


@commands.command()
async def hello(ctx):
    await ctx.send("Hammer is back!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"**[ERROR 404]** Please pass in all requirements :hammer_pick:. ```{error}```\nDo  {COMMAND_PREFIX}help command for more help"
        )
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "[**ERROR 403]** You dont the correct permission to do that :hammer:"
        )


@commands.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself")
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been banned from {ctx.guild.name} for {reason}"

    if not debug:
        await member.ban(reason=reason)
    descr = f"The user {member} has been banned for {reason}"
    embed = Embed(title=f"{member} has been banned! :hammer_pick:", description=descr)
    embed.set_image(url="https://i.imgflip.com/19zat3.jpg")
    embed.set_footer(
        text=f"Hammer | {ctx.message.author}",
        icon_url="https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670",
    )
    embed.set_thumbnail(url=member.avatar_url)
    await ctx.send(embed=embed)
    await member.send(message)


@commands.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.message.author:
        await ctx.channel.send("You cannot kick yourself")
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been kicked from {ctx.guild.name} for {reason}"
    if not debug:
        await member.kick(reason=reason)
    descr = f"The user {member} has been kicked for {reason}"
    embed = Embed(title=f"{member} has been kicked! :hammer_pick:", description=descr)
    embed.set_footer(
        text=f"Hammer | {ctx.message.author}",
        icon_url="https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670",
    )
    embed.set_thumbnail(url=member.avatar_url)
    # # embed.image = member.image
    await ctx.send(embed=embed)
    await member.send(message)


@commands.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    if member == ctx.message.author:
        await ctx.channel.send("You cannot warn yourself :(")
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been warned for {reason}"

    descr = f"The user {member} has been warned for {reason}"
    embed = Embed(title=f"{member} has been warned! :hammer_pick:", description=descr)
    embed.set_footer(
        text=f"Hammer | {ctx.message.author}",
        icon_url="https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670",
    )
    embed.set_thumbnail(url=member.avatar_url)

    await ctx.send(embed=embed)
    await member.send(message)


def resolve_variable(variable):
    if hasattr(variable, "__iter__"):
        var_length = len(list(variable))
        if (var_length > 100) and (not isinstance(variable, str)):
            return f"<a {type(variable).__name__} iterable with more than 100 values ({var_length})>"
        elif not var_length:
            return f"<an empty {type(variable).__name__} iterable>"

    if (not variable) and (not isinstance(variable, bool)):
        return f"<an empty {type(variable).__name__} object>"
    return (
        variable
        if (len(f"{variable}") <= 1000)
        else f"<a long {type(variable).__name__} object with the length of {len(f'{variable}'):,}>"
    )


@commands.command()
async def evaluate(ctx, *, code):
    if str(ctx.message.author.id) == str(OWNER):
        print("RECIEVED:", code)
        # t = ctx.message.author.id,"used the command eval at", datetime.now()
        # print(t)
        args = {
            "discord": discord,
            "sys": sys,
            "os": os,
            "imp": __import__,
            "ctx": ctx,
            "bot": bot,
        }
        try:
            exec(f"async def func(): return {code}", args)
            a = time()
            response = await eval("func()", args)
            await ctx.send(
                f"```py\n{response}```    |    ```{type(response).__name__}``` `| {(time() - a) / 1000} ms`"
            )
        except Exception as e:
            await ctx.send(f"Error occurred:```\n{type(e).__name__}: {str(e)}```")
    else:
        return


bot.add_command(evaluate)
bot.add_command(hello)
bot.add_command(kick)
bot.add_command(ban)
bot.add_command(warn)
bot.run(TOKEN)
