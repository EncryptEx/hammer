import discord, datetime, sys, os, git
from get_enviroment import (
    COMMAND_PREFIX,
    OWNER,
    TOKEN,
    ANNOUNCEMENTS_CHANNEL,
    SECURITY_CHANNEL,
    SWEAR_WORDS_LIST,
)
from discord import Embed
from discord.ext import commands
from discord.ext.commands.core import command
from time import time

# database import & connection
import sqlite3

conn = sqlite3.connect("maindatabase1.db")
cur = conn.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS `warns` (
	`userid` INT(100) UNIQUE,
	`warns` INT);"""
)

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
    """

    embed = Embed(
        title="Hammer Bot Help", description=descr, colour=discord.Colour.lighter_grey()
    )

    embed.add_field(
        name="Moderation Commands :tools:",
        value=f"""
    {COMMAND_PREFIX}ban [user] <reason>
    {COMMAND_PREFIX}kick [user] <reason>
    {COMMAND_PREFIX}warn [user] <reason>
    """,
        inline=True,
    )

    embed.add_field(
        name="AutoMod Services :robot:",
        value=f"Swear Word Detector and wuto warn.\n Using a +880 swear word database",
        inline=True,
    )

    embed.add_field(
        name="Chat Moderation Commands :file_folder:",
        value=f"""
    {COMMAND_PREFIX}setdelay [seconds] <reason>
    {COMMAND_PREFIX}mute [user] <reason>
    {COMMAND_PREFIX}unmute [user] <reason>
    """,
        inline=True,
    )

    embed.add_field(
        name="Various Utilities :screwdriver:",
        value=f"""
    {COMMAND_PREFIX}whois [user]
    """,
        inline=True,
    )

    embed.add_field(
        name="""Useful Links: :link:""",
        value=f"""[:classical_building: Hammer Bot Support](https://discord.gg/fMSyQA6)
    [:link: Hammer Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=591633652493058068&permissions=8&scope=bot)
    [:newspaper: Vote Hammer](https://top.gg/bot/591633652493058068)
    """,
        inline=True,
    )

    embed.add_field(
        name="Help Commands",
        value=f"""
    {COMMAND_PREFIX}help
    {COMMAND_PREFIX}invite
    """,
        inline=True,
    )

    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.message.author}", icon_url=hammericon
    )

    await ctx.send(embed=embed)


#
#   VARIOUS FUNCTIONS
#

# Function to alert the owner of something, normally to log use of eval command.
async def sendNotifOwner(text):
    await bot.get_channel(int(SECURITY_CHANNEL)).send(text)


# Function to add a warning and save it at the database
async def SetWarning(userid: int, substractMode: bool):
    cur.execute(f"SELECT * FROM warns WHERE userid={userid} LIMIT 1")
    rows = cur.fetchall()
    # print(rows)
    if len(rows) > 0:
        nwarns = rows[0][1]
        warn = nwarns+1 if substractMode else nwarns-1
        warn = 0 if warn <= 0 else warn
        cur.execute(f"UPDATE warns SET warns={warn} WHERE userid={userid}")
    else:
        initialwarn = 1 if (substractMode) else 0
        cur.execute(
            f"""INSERT OR IGNORE INTO warns (userid, warns)
            VALUES ({userid}, {initialwarn})
        """
    )
    conn.commit()
    return warn


# Function to create a template for all errors.
def ErrorEmbed(error):
    embed = Embed(title=f":no_entry_sign: Error!", description=error)

    embed.set_thumbnail(
        url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ficonsplace.com%2Fwp-content%2Fuploads%2F_icons%2Fff0000%2F256%2Fpng%2Ferror-icon-14-256.png&f=1&nofb=1"
    )

    embed.set_footer(
        text=f"Hammer",
        icon_url=hammericon,
    )
    return embed


#
# MAIN COMMANDS - BOT
#

# # swear words detector
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # Skip bot messages
    if message.author.bot:
        return
    words = message.content.split()
    for word in words:
        # print("scanning word:",word)
        word = str(word).lower()
        if word in SWEAR_WORDS_LIST:
            # print("detected word:",word)
            # print("user",message.author.name,"said",message.content)
            member = message.author
            # if member == .has perms :
            # return # is admin so don't warn it

            # maybe new function to optionally say the word (settings)
            descr = (
                f"The user {member} has been warned because said a banned swear word"
            )
            embed = Embed(
                title=f"{member} has been warned! :hammer_pick:", description=descr
            )
            embed.set_footer(
                text=f"Hammer | Command executed by {message.author}",
                icon_url=hammericon,
            )
            embed.set_thumbnail(url=member.avatar_url)
            warn = await SetWarning(member.id, True)
            s = "s" if warn > 1 else ""
            embed.add_field(name="Warn count", value=f"The user {member} has {warn} warn{s}. Be careful.", inline=True)
            bannedmessage = message.content[:message.content.find(word)]+"~~"+word+"~~"+message.content[message.content.find(word)+len(word):]
            embed.add_field(name="Message Removed:", value=f"The removed message was \n||{bannedmessage}||", inline=True)
            await message.channel.send(embed=embed)
            await message.delete()
            try:
                channel = await member.create_dm()
                await channel.send(embed=embed)

            except:
                await message.channel.send(
                    embed=ErrorEmbed(
                        f"Could not deliver the message to the user {member}\n This may be caused because the user is a bot, has blocked me or has the DMs turned off. \n\n**But the user is warned** and I have saved it into my beautiful unforgettable database"
                    )
                )
    # if(str(message.content).startswith(COMMAND_PREFIX)):
    # print("command executed", message.content)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="you")
    )
    print("HAMMER BOT Ready!", datetime.datetime.now())
    botname = await bot.application_info()
    print("logged in as:", botname.name)
    if botname.name == "Hammer":
        print("I'm on:")
        print(len(bot.guilds), "servers")
        print(sum(1 for x in bot.get_all_channels()), "channels")
        print(sum(1 for x in bot.get_all_members()), "members")
        chnl = bot.get_channel(int(ANNOUNCEMENTS_CHANNEL))
        await chnl.send("Bot UP!")
        print("Sent message to #" + str(chnl))


debug = False


@bot.command()
async def version(ctx):
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    await ctx.send("My version is " + sha)


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
    warn = await SetWarning(member.id, True)
    s = "s" if warn > 1 else ""
    embed.add_field(name="Warn count", value=f"The user {member} has {warn} warn{s}. Be careful.", inline=True)
    await ctx.send(embed=embed)
    try:
        await member.send(message)
    except:
        await ctx.send(
            embed=ErrorEmbed(
                f"Could not deliver the message to the user {member}\n This may be caused because the user is a bot, has blocked me or has the DMs turned off. \n\n**But the user is warned** and I have saved it into my beautiful unforgettable database"
            )
        )

@bot.command()
@commands.has_permissions(kick_members=True)
async def unwarn(ctx, member: discord.Member, *, reason=None):
    if reason == None:
        reason = "good behaviour ✅"
    message = f"You have been unwarned for {reason}"

    descr = f"The user {member} has been unwarned for {reason}"
    embed = Embed(title=f"{member} has been unwarned! :hammer_pick:", description=descr)
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.message.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.avatar_url)
    warn = await SetWarning(member.id, substractMode=False)
    s = "s" if warn > 1 else ""
    congrats = "Yey! :tada:" if warn == 0 else ""
    embed.add_field(name="Warn count", value=f"The user {member} has now {warn} warn{s}. {congrats}", inline=True)
    await ctx.send(embed=embed)
    try:
        await member.send(message)
    except:
        await ctx.send(
            embed=ErrorEmbed(
                f"Could not deliver the message to the user {member}\n This may be caused because the user is a bot, has blocked me or has the DMs turned off. \n\n**But the user is unwarned** and I have saved it into my beautiful unforgettable database"
            )
        )

@bot.command()
async def evaluate(ctx, *, code):
    if str(ctx.message.author.id) == str(OWNER):
        try:
            await sendNotifOwner(
                f"User {ctx.message.author} used command evaluate | id {ctx.message.author.id}"
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
        except Exception as e:
            await ctx.send(e)
    else:
        return


@bot.command()
@commands.has_permissions(manage_messages=True)
async def setdelay(ctx, seconds: float, *, reason=None):
    m = "modified" if seconds > 0.0 else "removed"
    embed = Embed(
        title=f"Delay {m} on #{ctx.channel} :hammer_pick:",
        description=f"This channel now has a delay of **{seconds}** seconds for {reason}"
        if reason != None and reason != ""
        else f"This channel now has a delay of **{seconds}** seconds",
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.message.author}",
        icon_url=hammericon,
    )

    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(embed=embed)


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
