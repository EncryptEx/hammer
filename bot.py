from email import message
from pydoc import describe
import discord, datetime, sys, os
from get_enviroment import (
    COMMAND_PREFIX,
    OWNER,
    TOKEN,
    ANNOUNCEMENTS_CHANNEL,
    DEV_SUGGESTIONS_CHANNEL,
    SECURITY_CHANNEL,
    SECURITY_GUILD,
    SWEAR_WORDS_LIST,
)
from discord import Embed, guild_only
from discord.ext import commands
from discord.commands import option
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
cur.execute(
    """CREATE TABLE IF NOT EXISTS `settings` (
        `guildid` INT(100) UNIQUE,
        `automod` INT);
        """
)

hammericon = "https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.AutoShardedBot(command_prefix=COMMAND_PREFIX, intents=intents)
client = discord.Client()

bot.remove_command("help")

#
#   HELP SECITON
#


@bot.slash_command(
    name="help", description="Displays all the available commands for Hammer"
)
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
    {COMMAND_PREFIX}unwarn [user] <reason>
    {COMMAND_PREFIX}clearwarns [user] <reason>
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
    {COMMAND_PREFIX}lock <channel> <reason>
    {COMMAND_PREFIX}unlock <channel> <reason>
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
    {COMMAND_PREFIX}suggest [suggestion]
    """,
        inline=True,
    )

    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}", icon_url=hammericon
    )

    await ctx.respond(embed=embed)


#
#   VARIOUS FUNCTIONS
#

# Function to alert the owner of something, normally to log use of eval command.
async def respondNotifOwner(text):
    await bot.get_channel(int(SECURITY_CHANNEL)).respond(text)


async def GetWarnings(userid: int):
    cur.execute("SELECT * FROM warns WHERE userid=? LIMIT 1", (userid,))
    rows = cur.fetchall()
    # print(rows)
    if len(rows) > 0:
        return rows[0][1]
    else:
        return 0


async def GetSettings(guildid: int):
    cur.execute("SELECT * FROM settings WHERE guildid=? LIMIT 1", (guildid,))
    rows = cur.fetchall()
    # print(rows)
    if len(rows) > 0:
        return rows[0][1]
    else:
        return 1  # By default is on


# Function to add a warning and save it at the database
async def SetWarning(
    userid: int, substractMode: bool, wantsToWipeAllWarns: bool = False
):
    cur.execute("SELECT * FROM warns WHERE userid=? LIMIT 1", (userid,))
    rows = cur.fetchall()
    # print(rows)
    if len(rows) > 0:
        nwarns = rows[0][1]
        warn = nwarns + 1 if substractMode else nwarns - 1
        warn = 0 if wantsToWipeAllWarns else warn
        warn = 0 if warn <= 0 else warn
        cur.execute("UPDATE warns SET warns=? WHERE userid=?", (warn, userid))
    else:
        initialwarn = 1 if (substractMode) else 0
        cur.execute(
            """INSERT OR IGNORE INTO warns (userid, warns)
            VALUES (?, ?)
        """,
            (userid, initialwarn),
        )
        warn = 1
    conn.commit()
    return warn


async def SaveSetting(guildid: int, module: str, value: int):

    # parse data
    guildid = str(guildid)
    module = str(module)
    value = str(value)
    cur.execute("SELECT * FROM settings WHERE guildid=? LIMIT 1", (guildid,))
    rows = cur.fetchall()
    # print(rows)
    if len(rows) > 0:  # cur.execute('INSERT INTO foo (a,b) values (?,?)', (strA, strB))
        cur.execute("""UPDATE settings 
        SET ?=? 
        WHERE guildid=? """,
        (module, value, guildid,))
    else:
        cur.execute(
            """INSERT OR IGNORE INTO settings (guildid, automod)
            VALUES (?,?) 
            """,
            (guildid, value,),
        )

    conn.commit()
    return


# Function to try to send a message to a user
async def SendMessageTo(ctx, member, message):
    try:
        await member.send(message)
    except:
        await ctx.respond(
            embed=ErrorEmbed(
                f"Could not deliver the message to the user {member}\n This may be caused because the user is a bot, has blocked me or has the DMs turned off. \n\n**But the user is warned** and I have saved it into my beautiful unforgettable database"
            ),
            ephemeral=True,
        )


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
    print("scanned: ", message.content)
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
                text=f"Hammer | Automod service",
                icon_url=hammericon,
            )
            embed.set_thumbnail(url=member.display_avatar)
            warn = await SetWarning(member.id, True)
            s = "s" if warn > 1 else ""
            embed.add_field(
                name="Warn count",
                value=f"The user {member} has {warn} warn{s}. Be careful.",
                inline=True,
            )
            bannedmessage = (
                message.content[: message.content.find(word)]
                + "~~"
                + word
                + "~~"
                + message.content[message.content.find(word) + len(word) :]
            )
            embed.add_field(
                name="Message Removed:",
                value=f"The removed message was \n||{bannedmessage}||",
                inline=True,
            )
            await message.channel.send(embed=embed)
            await message.delete()
            try:
                channel = await member.create_dm()
                await channel.send(embed=embed)

            except:
                embed = ErrorEmbed(
                    await message.channel.send(
                        f"Could not deliver the message to the user {member}\n This may be caused because the user is a bot, has blocked me or has the DMs turned off. \n\n**But the user is warned** and I have saved it into my beautiful unforgettable database"
                    ),
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


@bot.slash_command(guild_only=True, name="hello", guild_ids=[int(SECURITY_GUILD)])
async def hello(ctx):
    await ctx.respond("Hammer is back!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.respond(
            f"**[ERROR 404]** Please pass in all requirements :hammer_pick:. ```{error}```\nDo  {COMMAND_PREFIX}help command for more help",
            ephemeral=True,
        )
    if isinstance(error, commands.MissingPermissions):
        error = getattr(error, "original", error)
        missing = [
            perm.replace("_", " ").replace("guild", "server").title()
            for perm in error.missing_perms
        ]
        if len(missing) > 2:
            fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = " and ".join(missing)
        await ctx.respond(
            "[**ERROR 403**] You don't have the correct permission to do that :hammer:,  You need {fmt} permission(s) to perform this action",
            ephemeral=True,
        )


@bot.slash_command(
    guild_only=True,
    name="whois",
    description="Displays all the public info from a specific user",
)
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
            **Avatar URL:** [Click Here]({member.display_avatar})
            **Top role:** {member.top_role}
            **Warns:** {await GetWarnings(member.id)}
            """
        embed = Embed(title=f"Who is {member} ?", description=descr)

        embed.set_thumbnail(url=member.display_avatar)

        embed.set_footer(
            text=f"Hammer | Command executed by {ctx.author}",
            icon_url=hammericon,
        )
        await ctx.respond(embed=embed)
    except Exception as e:
        await ctx.respond(e)


@bot.slash_command(
    guild_only=True,
    name="ban",
    description="Keeps out a user permanently, forbidding its entry",
)
@discord.default_permissions(
    ban_members=True,
)
async def ban(ctx, member: discord.Member, *, reason=None):

    if member == ctx.author:
        await ctx.respond("You cannot ban yourself", ephemeral=True)
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been banned from {ctx.guild.name} for {reason}"

    descr = f"The user {member} has been banned for {reason}"
    embed = Embed(title=f"{member} has been banned! :hammer_pick:", description=descr)
    embed.set_image(url="https://i.imgflip.com/19zat3.jpg")
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    if not debug:
        try:
            await member.ban(reason=reason)
        except:
            ctx.respond(
                embed=ErrorEmbed(
                    f"Could not ban the user {member}\n This may be caused because I do not have the permission to do that or the user has a higher role than me."
                ),
                ephemeral=True,
            )
        return

    embed.set_thumbnail(url=member.display_avatar)
    await ctx.respond(embed=embed)
    await SendMessageTo(ctx, member, message)


@bot.slash_command(
    guild_only=True, name="kick", description="Kicks out a member from the server"
)
@discord.default_permissions(
    kick_members=True,
)
async def kick(ctx, member: discord.Member, *, reason=None):

    if member == ctx.author:
        await ctx.respond("You cannot kick yourself", ephemeral=True)
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been kicked from {ctx.guild.name} for {reason}"
    if not debug:
        try:
            await member.kick(reason=reason)
        except:
            ctx.respond(
                embed=ErrorEmbed(
                    f"Could not kick the user {member}\n This may be caused because I do not have the permission to do that or the user has a higher role than me."
                ),
                ephemeral=True,
            )
            return
    descr = f"The user {member} has been kicked for {reason}"
    embed = Embed(title=f"{member} has been kicked! :hammer_pick:", description=descr)
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    # # embed.image = member.image
    await ctx.respond(embed=embed)
    await SendMessageTo(ctx, member, message)


@bot.slash_command(
    guild_only=True,
    name="warn",
    description="Sets a warning for a user, at 3 warns/strikes they get kicked",
)
@discord.default_permissions(
    administrator=True,
)
async def warn(ctx, member: discord.Member, reason=None):

    if member == ctx.author:
        await ctx.respond("You cannot warn yourself :(", ephemeral=True)
        return
    if reason == None:
        reason = "bad behaviour 💥"
    message = f"You have been warned for {reason}"

    descr = f"The user {member} has been warned for {reason}"
    embed = Embed(title=f"{member} has been warned! :hammer_pick:", description=descr)
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await SetWarning(member.id, True)
    s = "s" if warn > 1 else ""
    embed.add_field(
        name="Warn count",
        value=f"The user {member} has {warn} warn{s}. Be careful.",
        inline=True,
    )
    await ctx.respond(embed=embed)

    await SendMessageTo(ctx, member, message)


@bot.slash_command(
    guild_only=True, name="unwarn", description="Removes a strike from a user"
)
@discord.default_permissions(
    kick_members=True,
)
async def unwarn(ctx, member: discord.Member, *, reason=None):

    if reason == None:
        reason = "good behaviour ✅"
    message = f"You have been unwarned for {reason}"

    descr = f"The user {member} has been unwarned for {reason}"
    embed = Embed(title=f"{member} has been unwarned! :hammer_pick:", description=descr)
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await SetWarning(member.id, substractMode=False)
    s = "s" if warn > 1 else ""
    congrats = "Yey! :tada:" if warn == 0 else ""
    embed.add_field(
        name="Warn count",
        value=f"The user {member} has now {warn} warn{s}. {congrats}",
        inline=True,
    )
    await ctx.respond(embed=embed)
    await SendMessageTo(ctx, member, message)


@bot.slash_command(
    guild_only=True, name="clearwarns", description="Removes all strikes from a user"
)
@discord.default_permissions(
    kick_members=True,
)
async def clearwarns(ctx, member: discord.Member, *, reason=None):

    if reason == None:
        reason = "good behaviour ✅"
    message = f"Your warns have been cleared for {reason}"

    descr = f"The user {member} has 0 warns for {reason}"
    embed = Embed(
        title=f"The warns of {member} have been removed! :hammer_pick:",
        description=descr,
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await SetWarning(member.id, substractMode=True, wantsToWipeAllWarns=True)
    embed.add_field(
        name="Warn count",
        value=f"The user {member} has now {warn} warns. Yey! :tada:",
        inline=True,
    )
    await ctx.respond(embed=embed, ephemeral=False)
    await SendMessageTo(ctx, member, message)


@bot.slash_command(guild_only=True, guild_ids=[int(SECURITY_GUILD)])
async def evaluate(ctx, code):

    if str(ctx.author.id) == str(OWNER):
        try:
            # await respondNotifOwner(
            #     f"User {ctx.author} used command evaluate | id {ctx.author.id}"
            # )
            print("RECIEVED:", code)
            # t = ctx.author.id,"used the command eval at", datetime.now()
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
                await ctx.respond(
                    f"```py\n{response}``````{type(response).__name__}``` `| {(time() - a) / 1000} ms`",
                    ephemeral=True,
                )
            except Exception as e:
                await ctx.respond(
                    f"Error occurred:```\n{type(e).__name__}: {str(e)}```",
                    ephemeral=True,
                )
        except Exception as e:
            await ctx.respond(e, ephemeral=True)
    else:
        await ctx.respond("you're not allowed to do that")


import sys


def restart_bot():
    os.execv(sys.executable, ["python"] + sys.argv)


@bot.slash_command(guild_only=True, guild_ids=[int(SECURITY_GUILD)])
async def restart(ctx):

    if str(ctx.author.id) == str(OWNER):
        try:
            # await respondNotifOwner(
            #     f"User {ctx.author} used command evaluate | id {ctx.author.id}"
            # )
            print("===== RESTART asked by", ctx.author, "=====")
            # t = ctx.author.id,"used the command eval at", datetime.now()
            # print(t)
            print("CLOSING SESSION")

            await bot.close()
            print("FETCHING NEW CHANGES IN GITHUB")
            import subprocess

            try:
                if not debug:
                    # Remove any changes done
                    res = subprocess.check_output(["git", "reset", "--hard"])
                    for line in res.splitlines():
                        print(line)
                    # Update files
                    res = subprocess.check_output(["git", "pull"])
                    for line in res.splitlines():
                        print(line)
            except Exception as e:
                await ctx.respond(e, ephemeral=True)
            print("===== STARTING BOT AGAIN =====")
            try:
                restart_bot()
            except Exception as e:
                print(e)
            await ctx.respond("Bot restarted successfully!", ephemeral=True)
        except Exception as e:
            await ctx.respond(e, ephemeral=True)
    else:
        await ctx.respond("you're not allowed to do that")


@bot.slash_command(
    guild_only=True,
    name="setdelay",
    description="Updates the message delay in a channel with a set of custom time interval",
)
@discord.default_permissions(
    manage_messages=True,
)
async def setdelay(ctx, seconds: float, reason: str = ""):

    m = "modified" if seconds > 0.0 else "removed"
    embed = Embed(
        title=f"Delay {m} on #{ctx.channel} :hammer_pick:",
        description=f"This channel now has a delay of **{seconds}** seconds for {reason}"
        if reason != None and reason != ""
        else f"This channel now has a delay of **{seconds}** seconds",
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )

    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.respond(embed=embed)


# description="Mutes the specified user."
@bot.slash_command(
    guild_only=True,
    name="mute",
    description="Removes the hability to talk or join voice channels to a user",
)
@discord.default_permissions(
    manage_messages=True,
)
async def mute(ctx, member: discord.Member, *, reason=None):

    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(
                mutedRole,
                speak=False,
                respond_messages=False,
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
    await ctx.respond(embed=embed)
    await member.add_roles(mutedRole, reason=reason)

    SendMessageTo(
        ctx,
        member,
        f":no_entry: You have been muted from: {ctx.guild.name} for {reason}",
    )


# description="Unmutes a specified user."
@bot.slash_command(
    guild_only=True,
    name="unmute",
    description="Restores the hability to talk or join voice channels to a user",
)
@discord.default_permissions(
    manage_messages=True,
)
async def unmute(ctx, member: discord.Member, *, reason=None):

    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    if reason == None:
        reason = " "
    else:
        reason = "for " + reason
    await member.remove_roles(mutedRole)
    SendMessageTo(
        ctx, member, f":tada: You have been unmuted from: {ctx.guild.name} {reason}"
    )
    embed = discord.Embed(
        title=f"User Unmuted: {member}",
        description=f"User {member.mention} has been unmuted {reason}",
        colour=discord.Colour.light_gray(),
    )
    await ctx.respond(embed=embed)


@discord.default_permissions(manage_channels=True)
@bot.slash_command(
    guild_only=True,
    name="lock",
    description="Blocks a channel from being used as a chat.",
)
async def lock(ctx, channel: discord.TextChannel = None, reason=None):

    channel = channel or ctx.channel
    reason = "for " + reason if reason else ""
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    embed = Embed(
        title=f"The channel #{ctx.channel} has been locked! :hammer_pick:",
        description=f"This channel is now locked {reason}",
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    await ctx.respond(embed=embed)


@discord.default_permissions(manage_channels=True)
@bot.slash_command(
    guild_only=True,
    name="unlock",
    description="Removes the blocking in a channel from not being used as a chat.",
)
async def unlock(ctx, channel: discord.TextChannel = None, reason=None):

    channel = channel or ctx.channel
    reason = "for " + reason if reason else ""
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    embed = Embed(
        title=f"The channel #{ctx.channel} has been unlocked! :hammer_pick:",
        description=f"This channel is now unlocked {reason}",
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    await ctx.respond(embed=embed)


@bot.slash_command(
    name="suggest",
    description="Sends a suggestion to the developer of Hammer.",
)
async def suggest(ctx, suggestion: str):

    embed = Embed(
        title=f"The user {ctx.author} has posted a suggestion! :hammer_pick:",
        description=f"{suggestion}",
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    suggestionChannel = bot.get_channel(int(DEV_SUGGESTIONS_CHANNEL))
    await suggestionChannel.send(embed=embed)
    await ctx.respond(
        "[200 OK] ✅ Your suggestion has been successfully recieved! \n Join our support server to see how does it progress! (in /help you'll find the link)",
        ephemeral=True,
    )


@bot.slash_command(
    name="invite",
    description="Returns the bot's invitation link.",
)
async def invite(ctx):
    embed = Embed(
        title=f"Invite Hammer Bot to your server! :hammer_pick:",
        description=f"[**🔗 Hammer Invite Link**](https://discordapp.com/api/oauth2/authorize?client_id=591633652493058068&permissions=8&scope=bot)",
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    await ctx.respond(embed=embed)


modules = ["automod"]


@discord.default_permissions(administrator=True)
@bot.slash_command(
    name="settings", description="Modifies some Hammer config values", guild_only=True
)
@option(
    "module",
    description="Pick a module to switch!",
    autocomplete=discord.utils.basic_autocomplete(modules),
)
@option(
    "value",
    description="Select on/off",
    autocomplete=discord.utils.basic_autocomplete(["on", "off"]),
)
async def settings(ctx, module: str = None, value: str = None):
    if module != None and value != None:
        if module in modules and value == "on" or value == "off":
            print("lets go")
            value = 1 if value == "on" else 0
            await SaveSetting(ctx.guild.id, module, value)
            action = "enabled" if value else "disabled"
            await ctx.respond(f"Module {module} {action} successfully!", ephemeral=True)
            return
        else:
            await ctx.respond("Use: ``/settings module on/off``", ephemeral=True)
            return
    embed = Embed(
        title=f"Hammer Bot Settings :hammer_pick:",
        description=f"Here you can enable or disable some modules",
    )
    print("getting settings from discord.Guild.id", ctx.guild.id)
    automodStatus = await GetSettings(ctx.guild.id)
    automodStatustr = "**✅ ON**" if automodStatus else "**❌ OFF**"
    recommendedactivityAutomod = (
        f"Disable it by doing: ``{COMMAND_PREFIX}settings automod off``"
        if automodStatus
        else f"Enable it by doing ``{COMMAND_PREFIX}settings automod on``"
    )
    embed.add_field(
        name="AutoMod Services :robot:",
        value=f"Actual status: {automodStatustr}\n {recommendedactivityAutomod}",
        inline=True,
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    await ctx.respond(embed=embed)


bot.run(TOKEN)
