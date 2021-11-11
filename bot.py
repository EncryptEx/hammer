import discord
from discord import embeds
from get_enviroment import (
    COMMAND_PREFIX,
    OWNER,
    TOKEN,
    ANNOUNCEMENTS_CHANNEL,
    SECURITY_CHANNEL,
)
from discord import Embed
from discord.ext import commands
from discord.ext.commands.core import command
from time import time
import datetime
import sys
import os

import datetime

hammericon = "https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670"

intents = discord.Intents.default()
# intents.members = True
# intents.messages = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

bot.remove_command("help")

#
#   HELP SECITON
#


@bot.command()
async def help(ctx):
    # Define each page

    descr = f"""Hammer is a multiuse bot focused on moderation, which its goal is to improve your discord community.    
    For an extense command description, use ``{COMMAND_PREFIX}help [command name]`` (comming soon)
    **Hammer's commands:**
    {COMMAND_PREFIX}help
    {COMMAND_PREFIX}whois [user]
    {COMMAND_PREFIX}ban [user] <reason>
    {COMMAND_PREFIX}kick [user] <reason>
    {COMMAND_PREFIX}warn [user] <reason>
    {COMMAND_PREFIX}mute [user] <reason>
    {COMMAND_PREFIX}unmute [user] <reason>
    
    **Useful Link:**
    [Hammer Bot Support](https://discord.gg/fMSyQA6)
    [Hammer Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=591633652493058068&permissions=8&scope=bot)
    """
    embed = Embed(title="Hammer Bot Help", description=descr, colour=discord.Colour.lighter_grey())

    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.message.author}", icon_url=hammericon
    )

    await ctx.send(embed=embed)


def sendNotifOwner(text):
    bot.get_channel(SECURITY_CHANNEL).send(text)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="you")
    )
    print("HAMMER BOT Ready!", datetime.datetime.now())
    print("I'm on:")
    print(len(bot.guilds), "servers")
    print(sum(1 for x in bot.get_all_channels()), "channels")
    print(sum(1 for x in bot.get_all_members()), "members")
    botname = await bot.application_info()
    print("logged in as:", botname.name)
    if botname.name == "Hammer":
        chnl = bot.get_channel(int(ANNOUNCEMENTS_CHANNEL))
        await chnl.send("Bot UP!")
        print("Sent message to #" + str(chnl))


debug = False


@bot.command()
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
            "[**ERROR 403]** You don't have the correct permission to do that :hammer:"
        )


@bot.command()
async def whois(ctx, member: discord.Member):
    try:
        username, discriminator = str(member).split("#")
        isbot = ":white_check_mark:" if member.bot else ":negative_squared_cross_mark:"
        descr = f"""
            **Nick:** {member.nick}
            **Username:** {username}
            **Discriminator:** {discriminator}
            **Created account at:** {member.created_at}
            **Joined server at:** {member.joined_at}
            **Is bot:** {isbot}
            **User ID:** {member.id}
            **Avatar URL:** [Click Here]({member.avatar_url})
            **Top role:** {member.top_role}
            """
        embed = Embed(title=f"Who is {member} ?", description=descr)

        embed.set_thumbnail(url=member.avatar_url)

        embed.set_footer(
            text=f"Hammer | Command executed by {ctx.message.author}",
            icon_url=hammericon,
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(e)


@bot.command()
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
        text=f"Hammer | Command executed by {ctx.message.author}",
        icon_url=hammericon,
    )

    embed.set_thumbnail(url=member.avatar_url)
    await ctx.send(embed=embed)
    await member.send(message)


@bot.command()
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
        text=f"Hammer | Command executed by {ctx.message.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.avatar_url)
    # # embed.image = member.image
    await ctx.send(embed=embed)
    await member.send(message)


@bot.command()
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
        text=f"Hammer | Command executed by {ctx.message.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.avatar_url)

    await ctx.send(embed=embed)
    await member.send(message)


@bot.command()
async def evaluate(ctx, *, code):
    if str(ctx.message.author.id) == str(OWNER):
        sendNotifOwner(
            "User with "
            + ctx.message.author
            + " used command evaluate | id "
            + ctx.message.author.id
        )
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
                f"```py\n{response}``````{type(response).__name__}``` `| {(time() - a) / 1000} ms`"
            )
        except Exception as e:
            await ctx.send(f"Error occurred:```\n{type(e).__name__}: {str(e)}```")
    else:
        return


# description="Mutes the specified user."
@bot.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(
                mutedRole,
                speak=False,
                send_messages=False,
                read_message_history=True,
                read_messages=False,
            )

    if reason == None:
        reason = "bad behaviour 💥"

    embed = discord.Embed(
        title=f"User Muted: {member}",
        description=f"User {member.mention} has been muted for {reason}",
        colour=discord.Colour.red(),
    )
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)

    try:
        await member.send(
            f":no_entry: You have been muted from: {ctx.guild.name} for {reason}"
        )
    except:
        await ctx.send(f"Could not sent a message to the user {member.mention}")


# description="Unmutes a specified user."
@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member, *, reason=None):

    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    if reason == None:
        reason = " "
    else:
        reason = "for " + reason
    await member.remove_roles(mutedRole)
    try:
        await member.send(
            f":tada: You have been unmuted from: {ctx.guild.name} {reason}"
        )
    except:
        await ctx.send(f"Could not sent a message to the user {member.mention}")
    embed = discord.Embed(
        title=f"User Unmuted: {member}",
        description=f"User {member.mention} has been unmuted {reason}",
        colour=discord.Colour.light_gray(),
    )
    await ctx.send(embed=embed)


bot.run(TOKEN)
