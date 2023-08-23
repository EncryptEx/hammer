import datetime
import os
import sqlite3
import sys
import urllib
from email import message
from pydoc import describe
from time import time

import discord
from discord import Embed, guild_only
from discord.commands import option
from discord.ext import commands
from discord.ext.commands.core import command
from quickchart import QuickChart

from get_enviroment import (ANNOUNCEMENTS_CHANNEL, COMMAND_PREFIX,
                            DEV_SUGGESTIONS_CHANNEL, OWNER, SECURITY_CHANNEL,
                            SECURITY_GUILD, SWEAR_WORDS_LIST, TOKEN)

# database import & connection

conn = sqlite3.connect("maindatabase1.db")
cur = conn.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS `warns` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `userid` INT(100),
        `guildid` INT,
        `reason` TEXT,
        `timestamp` INT);
        """
)
cur.execute(
    """CREATE TABLE IF NOT EXISTS `customWords` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `guildid` INT,
        `uploaderId`INT,
        `word` TEXT,
        `type` INT);
        """
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
    {COMMAND_PREFIX}softwarn [user] <reason>
    {COMMAND_PREFIX}unwarn [user] [id] <reason>
    {COMMAND_PREFIX}clearwarns [user] <reason>
    {COMMAND_PREFIX}seewarns [user]
    """,
        inline=True,
    )

    embed.add_field(
        name="AutoMod Services :robot:",
        value=f"""Swear Word Detector and wuto warn.
Using a +880 swear word database

Customize it with:
{COMMAND_PREFIX}automod [add/remove] [word]
Or switch it on/off with:
{COMMAND_PREFIX}settings [automod] [on/off]""",
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


async def GetWarnings(userid: int, guildid: int, fullData: bool = False):
    cur.execute(
        "SELECT * FROM warns WHERE userid=? AND guildid=?",
        (
            userid,
            guildid,
        ),
    )
    rows = cur.fetchall()
    if not fullData:
        return len(rows)
    else:
        return rows


# Function to add a warning and save it at the database
async def AddWarning(userid: int, guildid: int, reason):
    warncount = await GetWarnings(userid, guildid)
    cur.execute(
        """INSERT OR IGNORE INTO warns (userid, guildid, reason, timestamp)
        VALUES (?, ?, ?, ?)
    """,
        (userid, guildid, reason, time()),
    )
    conn.commit()
    return warncount + 1


async def Removewarn(userid: int, guildId: int, relativeWarnId: int):
    c = 0
    for warn in await GetWarnings(userid, guildId, fullData=True):
        warnRealId, _, _, SubReason, _ = warn
        if c == relativeWarnId:
            # delete that row
            cur.execute(
                "DELETE FROM warns WHERE userid=? AND guildid=? AND id=? LIMIT 1",
                (userid, guildId, warnRealId),
            )
        c = c + 1
    conn.commit()
    return c - 1


async def Clearwarns(userid: int, guildId: int):
    # delete all rows
    cur.execute("DELETE FROM warns WHERE userid=? AND guildid=?", (userid, guildId))
    conn.commit()
    return


async def getAllWarns(userid: int, guildid: int):
    allwarns = []
    c = 0
    for warn in await GetWarnings(userid, guildid, fullData=True):
        _, _, _, SubReason, timestamp = warn
        dt = timestamp
        if c <= 9:
            emojis = ":" + numToEmoji(c) + ":"
        else:
            emojis = str(c)
        ddt = int(str(dt)[: str(dt).find(".")])
        allwarns.append(f"- **ID: {emojis}** Reason: ``{SubReason}``  <t:{ddt}:R>")

        c = c + 1
    return allwarns


async def GetAutomodCustomWords(guildid: int, mode: str):
    wtype = 1 if mode == "allow" else 0
    cur.execute(
        "SELECT word FROM customWords WHERE guildid = ? AND type = ?", (guildid, wtype)
    )
    words = cur.fetchall()
    a = []
    if len(words) > 0:
        for word in words:
            a.append(str(word[0]))
        return a
    else:
        return []  # default is emptys


async def AddAllowedWord(guildid: int, userid: int, word: str):
    # check if user is in blacklist
    # if(word in await GetAutomodCustomWords(guildid, "deny")):

    try:
        cur.execute(
            """DELETE FROM customWords WHERE guildid=? AND word=? AND type=0
        """,
            (guildid, word),
        )

        cur.execute(
            """INSERT OR IGNORE INTO customWords (id, guildid, uploaderId, word, type)
            VALUES (NULL, ?, ?, ?, 1)
        """,
            (guildid, userid, word),
        )
        conn.commit()
    except:
        return False
    return True


async def AddDeniedWord(guildid: int, userid: int, word: str):
    try:
        cur.execute(
            """DELETE FROM customWords WHERE guildid=? AND word=? AND type=1
        """,
            (guildid, word),
        )

        cur.execute(
            """INSERT OR IGNORE INTO customWords (id, guildid, uploaderId, word, type)
            VALUES (NULL, ?, ?, ?, 0)
        """,
            (guildid, userid, word),
        )
        conn.commit()
    except:
        return False
    return True


async def GetSettings(guildid: int):
    cur.execute("SELECT * FROM settings WHERE guildid = ? LIMIT 1", (guildid,))
    rows = cur.fetchall()
    if len(rows) > 0:
        return rows[0][1]
    else:
        return 0  # default is off


async def SaveSetting(guildid: int, module: str, value: int):
    cur.execute("SELECT * FROM settings WHERE guildid = ? LIMIT 1", (guildid,))
    rows = cur.fetchall()
    # print(rows)
    if len(rows) > 0:  # cur.execute('INSERT INTO foo (a,b) values (?,?)', (strA, strB))
        query = f"""UPDATE settings
        SET automod = {value}
        WHERE guildid={guildid} """
        cur.execute(query)
    else:
        cur.execute(
            """INSERT OR IGNORE INTO settings (guildid, automod)
            VALUES (?,?)
            """,
            (
                guildid,
                value,
            ),
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


def unicodeLetterConver(word):
    f = ""
    normalAlph = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
    alphs = [
        "𝐀𝐚𝐁𝐛𝐂𝐜𝐃𝐝𝐄𝐞𝐅𝐟𝐆𝐠𝐇𝐡𝐈𝐢𝐉𝐣𝐊𝐤𝐋𝐥𝐌𝐦𝐍𝐧𝐎𝐨𝐏𝐩𝐐𝐪𝐑𝐫𝐒𝐬𝐓𝐭𝐔𝐮𝐕𝐯𝐖𝐰𝐗𝐱𝐘𝐲𝐙𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
        "𝕬𝖆𝕭𝖇𝕮𝖈𝕯𝖉𝕰𝖊𝕱𝖋𝕲𝖌𝕳𝖍𝕴𝖎𝕵𝖏𝕶𝖐𝕷𝖑𝕸𝖒𝕹𝖓𝕺𝖔𝕻𝖕𝕼𝖖𝕽𝖗𝕾𝖘𝕿𝖙𝖀𝖚𝖁𝖛𝖂𝖜𝖃𝖝𝖄𝖞𝖅𝖟",
        "𝑨𝒂𝑩𝒃𝑪𝒄𝑫𝒅𝑬𝒆𝑭𝒇𝑮𝒈𝑯𝒉𝑰𝒊𝑱𝒋𝑲𝒌𝑳𝒍𝑴𝒎𝑵𝒏𝑶𝒐𝑷𝒑𝑸𝒒𝑹𝒓𝑺𝒔𝑻𝒕𝑼𝒖𝑽𝒗𝑾𝒘𝑿𝒙𝒀𝒚𝒁𝒛",
        "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
        "🄰🄰🄱🄱🄲🄲🄳🄳🄴🄴🄵🄵🄶🄶🄷🄷🄸🄸🄹🄹🄺🄺🄻🄻🄼🄼🄽🄽🄾🄾🄿🄿🅀🅀🅁🅁🅂🅂🅃🅃🅄🅄🅅🅅🅆🅆🅇🅇🅈🅈🅉🅉0123456789",
        "🅰🅰🅱🅱🅲🅲🅳🅳🅴🅴🅵🅵🅶🅶🅷🅷🅸🅸🅹🅹🅺🅺🅻🅻🅼🅼🅽🅽🅾🅾🅿🅿🆀🆀🆁🆁🆂🆂🆃🆃🆄🆄🆅🆅🆆🆆🆇🆇🆈🆈🆉🆉𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
        "ⒶⓐⒷⓑⒸⓒⒹⓓⒺⓔⒻⓕⒼⓖⒽⓗⒾⓘⒿⓙⓀⓚⓁⓛⓂⓜⓃⓝⓄⓞⓅⓟⓆⓠⓇⓡⓈⓢⓉⓣⓊⓤⓋⓥⓌⓦⓍⓧⓎⓨⓏⓩ0①②③④⑤⑥⑦⑧⑨",
        "🅐🅐🅑🅑🅒🅒🅓🅓🅔🅔🅕🅕🅖🅖🅗🅗🅘🅘🅙🅙🅚🅚🅛🅛🅜🅜🅝🅝🅞🅞🅟🅟🅠🅠🅡🅡🅢🅢🅣🅣🅤🅤🅥🅥🅦🅦🅧🅧🅨🅨🅩🅩𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
        "ᗩᗩᗷᗷᑕᑕᗪᗪEEᖴᖴGGᕼᕼIIᒍᒍKKᒪᒪᗰᗰᑎᑎOOᑭᑭᑫᑫᖇᖇᔕᔕTTᑌᑌᐯᐯᗯᗯ᙭᙭YYᘔᘔ0123456789",
        "𝗔𝗮𝗕𝗯𝗖𝗰𝗗𝗱𝗘𝗲𝗙𝗳𝗚𝗴𝗛𝗵𝗜𝗶𝗝𝗷𝗞𝗸𝗟𝗹𝗠𝗺𝗡𝗻𝗢𝗼𝗣𝗽𝗤𝗾𝗥𝗿𝗦𝘀𝗧𝘁𝗨𝘂𝗩𝘃𝗪𝘄𝗫𝘅𝗬𝘆𝗭𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
        "𝘼𝙖𝘽𝙗𝘾𝙘𝘿𝙙𝙀𝙚𝙁𝙛𝙂𝙜𝙃𝙝𝙄𝙞𝙅𝙟𝙆𝙠𝙇𝙡𝙈𝙢𝙉𝙣𝙊𝙤𝙋𝙥𝙌𝙦𝙍𝙧𝙎𝙨𝙏𝙩𝙐𝙪𝙑𝙫𝙒𝙬𝙓𝙭𝙔𝙮𝙕𝙯𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
        "𝘈𝘢𝘉𝘣𝘊𝘤𝘋𝘥𝘌𝘦𝘍𝘧𝘎𝘨𝘏𝘩𝘐𝘪𝘑𝘫𝘒𝘬𝘓𝘭𝘔𝘮𝘕𝘯𝘖𝘰𝘗𝘱𝘘𝘲𝘙𝘳𝘚𝘴𝘛𝘵𝘜𝘶𝘝𝘷𝘞𝘸𝘟𝘹𝘠𝘺𝘡𝘻0123456789",
        "ＡａＢｂＣｃＤｄＥｅＦｆＧｇＨｈＩｉＪｊＫｋＬｌＭｍＮｎＯｏＰｐＱｑＲｒＳｓＴｔＵｕＶｖＷｗＸｘＹｙＺｚ０１２３４５６７８９",
        "⒜⒜⒝⒝⒞⒞⒟⒟⒠⒠⒡⒡⒢⒢⒣⒣⒤⒤⒥⒥⒦⒦⒧⒧⒨⒨⒩⒩⒪⒪⒫⒫⒬⒬⒭⒭⒮⒮⒯⒯⒰⒰⒱⒱⒲⒲⒳⒳⒴⒴⒵⒵0⑴⑵⑶⑷⑸⑹⑺⑻⑼",
        "𝙰𝚊𝙱𝚋𝙲𝚌𝙳𝚍𝙴𝚎𝙵𝚏𝙶𝚐𝙷𝚑𝙸𝚒𝙹𝚓𝙺𝚔𝙻𝚕𝙼𝚖𝙽𝚗𝙾𝚘𝙿𝚙𝚀𝚚𝚁𝚛𝚂𝚜𝚃𝚝𝚄𝚞𝚅𝚟𝚆𝚠𝚇𝚡𝚈𝚢𝚉𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
        "𝖠𝖺𝖡𝖻𝖢𝖼𝖣𝖽𝖤𝖾𝖥𝖿𝖦𝗀𝖧𝗁𝖨𝗂𝖩𝗃𝖪𝗄𝖫𝗅𝖬𝗆𝖭𝗇𝖮𝗈𝖯𝗉𝖰𝗊𝖱𝗋𝖲𝗌𝖳𝗍𝖴𝗎𝖵𝗏𝖶𝗐𝖷𝗑𝖸𝗒𝖹𝗓𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫",
        "🇦🇦🇧🇧🇨🇨🇩🇩🇪🇪🇫🇫🇬🇬🇭🇭🇮🇮🇯🇯🇰🇰🇱🇱🇲🇲🇳🇳🇴🇴🇵🇵🇶🇶🇷🇷🇸🇸🇹🇹🇺🇺🇻🇻🇼🇼🇽🇽🇾🇾🇿🇿0123456789",
        "คค๖๖¢¢໓໓ēēffງງhhiiววkkll๓๓ຖຖ໐໐pp๑๑rrŞŞttนนงงຟຟxxฯฯຊຊ0123456789",
        "₳₳฿฿₵₵ĐĐɆɆ₣₣₲₲ⱧⱧłłJJ₭₭ⱠⱠ₥₥₦₦ØØ₱₱QQⱤⱤ₴₴₮₮ɄɄVV₩₩ӾӾɎɎⱫⱫ0123456789",
        "卂卂乃乃匚匚ᗪᗪ乇乇千千ᎶᎶ卄卄丨丨ﾌﾌҜҜㄥㄥ爪爪几几ㄖㄖ卩卩ɊɊ尺尺丂丂ㄒㄒㄩㄩᐯᐯ山山乂乂ㄚㄚ乙乙0123456789",
        "ꭿaꞴꞵꞒꞓDdEꬲꟻꝭGgꞪꜧIꭵꞲjꞢꞣꝆꝇMꝳꞐꝴꝊꭴꝔꝓꝖꝙꮢꞧꞨꞩꮦtUuꝞꝟꝠꝡꭓꭗꝨꝩZz0123456789",
        "ДӓѢѣҀҁDdЗЭFfGgњћIїJjККLlMmЙђФѳPpQqЯГSsҬҭЦЧVѵШШЖxӲӳZz0123456789",
        "ᴀᴀʙʙᴄᴄᴅᴅᴇᴇꜰꜰɢɢʜʜɪɪᴊᴊᴋᴋʟʟᴍᴍɴɴᴏᴏᴩᴩQqʀʀꜱꜱᴛᴛᴜᴜᴠᴠᴡᴡxxYyᴢᴢ0123456789",
        "ₐₐBbCcDdₑₑFfGgₕₕᵢᵢⱼⱼₖₖₗₗₘₘₙₙₒₒₚₚQqᵣᵣₛₛₜₜᵤᵤᵥᵥWwₓₓYyZz₀₁₂₃₄₅₆₇₈₉",
        "ᴬᵃᴮᵇᶜᶜᴰᵈᴱᵉᶠᶠᴳᵍᴴʰᴵⁱᴶʲᴷᵏᴸˡᴹᵐᴺⁿᴼᵒᴾᵖQqᴿʳˢˢᵀᵗᵁᵘⱽᵛᵂʷˣˣʸʸᶻᶻ⁰¹²³⁴⁵⁶⁷⁸⁹",
        "ΔΔββĆĆĐĐ€€₣₣ǤǤĦĦƗƗĴĴҜҜŁŁΜΜŇŇØØƤƤΩΩŘŘŞŞŦŦỮỮVVŴŴЖЖ¥¥ŽŽ0123456789",
        "ααɓɓ૮૮∂∂εεƒƒɠɠɦɦเเʝʝҡҡℓℓɱɱɳɳσσρρφφ૨૨รรƭƭµµѵѵωωאאყყƶƶ0123456789",
    ]
    for l in word:
        if l in normalAlph:
            f = f + l
            continue
        for alphabet in alphs:
            pos = alphabet.find(l)
            if pos != -1:
                print("found", f)
                f = f + normalAlph[pos]
                break
    return f


def numToEmoji(num):
    v = ""
    if num == 0:
        v = "zero"
    if num == 1:
        v = "one"
    if num == 2:
        v = "two"
    if num == 3:
        v = "three"
    if num == 4:
        v = "four"
    if num == 5:
        v = "five"
    if num == 6:
        v = "six"
    if num == 7:
        v = "seven"
    if num == 8:
        v = "eight"
    if num == 9:
        v = "nine"
    return v


def filterMember(member: discord.Member):
    username, discriminator = str(member).split("#")
    if discriminator == "0":
        return username
    return str(member)


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
    if message.content == "" or message.content == None:
        return
    if int(await GetSettings(message.guild.id)) != 1:
        return  # user has disabled Automod
    words = message.content.split()
    allowed_words_guild_list = await GetAutomodCustomWords(message.guild.id, "allow")
    denied_words_guild_list = await GetAutomodCustomWords(message.guild.id, "deny")
    print("scanned: ", message.content)
    for word in words:
        # print("scanning word:",word)
        originalWord = str(word).lower()
        word = unicodeLetterConver(str(word).lower())
        if word in allowed_words_guild_list:
            continue

        if word in denied_words_guild_list or word in SWEAR_WORDS_LIST:
            member = message.author
            # if member == .has perms :
            # return # is admin so don't warn it

            # maybe new function to optionally say the word (settings)
            descr = f"The user {filterMember(member)} has been warned because said a banned swear word"
            embed = Embed(
                title=f"{filterMember(member)} has been warned! :hammer_pick:",
                description=descr,
            )
            embed.set_footer(
                text=f"Hammer | Automod service",
                icon_url=hammericon,
            )
            embed.set_thumbnail(url=member.display_avatar)
            warn = await AddWarning(
                member.id, message.guild.id, "Said a banned swear word"
            )
            s = "s" if warn > 1 else ""
            embed.add_field(
                name="Warn count",
                value=f"The user {filterMember(member)} has {warn} warn{s}. Be careful. Run /seewarns @user to check its warnhistory",
                inline=True,
            )
            bannedmessage = (
                message.content[: message.content.find(originalWord)]
                + "~~"
                + word
                + "~~"
                + message.content[message.content.find(originalWord) + len(word) :]
            )
            embed.add_field(
                name="Message Removed:",
                value=f"The removed message was \n||{bannedmessage}||",
                inline=True,
            )
            embed.add_field(
                name="Not happy with this?",
                value=f"Disable this feature with ``/settings automod off`` or simply ``/suggest``  a new change",
                inline=False,
            )
            await message.channel.send(embed=embed)
            await message.delete()
            try:
                channel = await member.create_dm()
                await channel.send(embed=embed)

            except:
                embed = ErrorEmbed(
                    await message.channel.send(
                        f"Could not deliver the message to the user {filterMember(member)}\n This may be caused because the user is a bot, has blocked me or has the DMs turned off. \n\n**But the user is warned** and I have saved it into my beautiful unforgettable database"
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
        discriminator = "" if discriminator == "0" else discriminator
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
            **Warns:** {await GetWarnings(member.id, ctx.guild.id)}
            """
        embed = Embed(title=f"Who is {filterMember(member)} ?", description=descr)

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

    descr = f"The user {filterMember(member)} has been banned for {reason}"
    embed = Embed(
        title=f"{filterMember(member)} has been banned! :hammer_pick:",
        description=descr,
    )
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
                    f"Could not ban the user {filterMember(member)}\n This may be caused because I do not have the permission to do that or the user has a higher role than me."
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
                    f"Could not kick the user {filterMember(member)}\n This may be caused because I do not have the permission to do that or the user has a higher role than me."
                ),
                ephemeral=True,
            )
            return
    descr = f"The user {filterMember(member)} has been kicked for {reason}"
    embed = Embed(
        title=f"{filterMember(member)} has been kicked! :hammer_pick:",
        description=descr,
    )
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
@option(
    "softwarn",
    description="Select on/off",
    autocomplete=discord.utils.basic_autocomplete(["on", "off"]),
)
@discord.default_permissions(
    administrator=True,
)
async def warn(ctx, member: discord.Member, reason=None, softwarn: bool = False):
    if member == ctx.author:
        await ctx.respond("You cannot warn yourself :(", ephemeral=True)
        return
    if reason == None:
        reason = "bad behaviour 💥"

    message = f"You have been warned for {reason}"

    descr = f"The user {filterMember(member)} has been warned for {reason}"
    embed = Embed(
        title=f"{filterMember(member)} has been warned! :hammer_pick:",
        description=descr,
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await AddWarning(member.id, ctx.guild.id, reason)
    s = "s" if warn > 1 else ""
    embed.add_field(
        name="Warn count",
        value=f"The user {filterMember(member)} has {warn} warn{s}. Be careful.",
        inline=True,
    )
    await ctx.respond(embed=embed, ephemeral=softwarn)

    if not softwarn:
        await SendMessageTo(ctx, member, message)


@bot.slash_command(
    guild_only=True,
    name="softwarn",
    description="Sets a silent warning for a user, at 3 warns/strikes they get kicked",
)
@discord.default_permissions(
    administrator=True,
)
async def softwarn(ctx, member: discord.Member, reason=None):
    await warn(ctx, member, reason, True)


@bot.slash_command(
    guild_only=True,
    name="seewarns",
    description="Displays the warn history of a user in the guild",
)
@discord.default_permissions(
    administrator=True,
)
async def seewarns(ctx, member: discord.Member):
    allwarns = await getAllWarns(member.id, ctx.guild.id)
    if len(allwarns) == 0:
        allwarns = ["User had no warns at the moment"]
    message = "\n".join(allwarns)

    c = 0
    data = []
    for warn in await GetWarnings(member.id, ctx.guild.id, fullData=True):
        _, _, _, _, timestamp = warn
        c = c + 1
        data.append(
            {
                "t": str(
                    datetime.datetime.fromtimestamp(
                        int(str(timestamp)[: str(timestamp).find(".")])
                    )
                ),
                "y": c,
            }
        )

    qc = QuickChart()
    qc.width = 500
    qc.height = 300
    qc.device_pixel_ratio = 2.0
    qc.config = {
        "type": "line",
        "data": {
            "datasets": [
                {
                    "fill": False,
                    "label": [f"Warns of {filterMember(member)}"],
                    "lineTension": 0,
                    "backgroundColor": "#7289DA",
                    "borderColor": "#7289DA",
                    "data": data,
                }
            ]
        },
        "options": {
            "scales": {
                "xAxes": [
                    {
                        "type": "time",
                        "time": {
                            "parser": "YYYY-MM-DD HH:mm:ss",
                            "displayFormats": {"day": "DD/MM/YYYY"},
                        },
                    }
                ]
            }
        },
    }

    uurl = qc.get_url()

    embed = Embed(title=f"**Historic of {filterMember(member)}**", description=message)
    embed.set_image(url=uurl)
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    return await ctx.respond(embed=embed)


@bot.slash_command(
    guild_only=True, name="unwarn", description="Removes a strike from a user"
)
@discord.default_permissions(
    kick_members=True,
)
async def unwarn(ctx, member: discord.Member, id: int = None, *, reason=None):
    if await GetWarnings(member.id, ctx.guild.id) == 0:
        return await ctx.respond("This user does not have any warn!")
    if id == None:
        message = (
            f"""To select a warn to remove, use argument id and specify its value."""
        )

        embed = Embed(
            title=f"ERROR! Need to select a warn :hammer_pick:", description=message
        )
        allwarns = await getAllWarns(member.id, ctx.guild.id)
        embed.add_field(
            name=f"**Historic of {member.name}**:",
            value="\n".join(allwarns),
        )
        return await ctx.respond(embed=embed)
    if reason == None:
        reason = "good behaviour ✅"
    message = f"You have been unwarned for {reason}"

    descr = f"The user {filterMember(member)} has been unwarned for {reason}"
    embed = Embed(
        title=f"{filterMember(member)} has been unwarned! :hammer_pick:",
        description=descr,
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await Removewarn(member.id, ctx.guild.id, id)
    s = "s" if warn > 1 else ""
    congrats = "Yey! :tada:" if warn == 0 else ""
    embed.add_field(
        name="Warn count",
        value=f"The user {filterMember(member)} has now {warn} warn{s}. {congrats}",
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

    descr = f"The user {filterMember(member)} has 0 warns for {reason}"
    embed = Embed(
        title=f"The warns of {filterMember(member)} have been removed! :hammer_pick:",
        description=descr,
    )
    embed.set_footer(
        text=f"Hammer | Command executed by {ctx.author}",
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await Clearwarns(member.id, ctx.guild.id)
    embed.add_field(
        name="Warn count",
        value=f"The user {filterMember(member)} has now {warn} warns. Yey! :tada:",
        inline=True,
    )
    await ctx.respond(embed=embed, ephemeral=False)
    await SendMessageTo(ctx, member, message)


@bot.slash_command(
    guild_only=True,
    name="automod",
    description="Customizes in this guild Hammer's automod",
)
@discord.default_permissions(
    administrator=True,
)
@option(
    "action",
    description="Select add/remove word from swear list",
    autocomplete=discord.utils.basic_autocomplete(["add", "remove"]),
)
async def automod(ctx, action: str, word: str):
    if action == "remove":
        response = await AddAllowedWord(ctx.guild.id, ctx.author.id, word)
    elif action == "add":
        response = await AddDeniedWord(ctx.guild.id, ctx.author.id, word)
    else:
        return await ctx.respond(
            embed=ErrorEmbed("Wrong syntax, please use /automod add/remove [word]"),
            ephemeral=True,
        )
    if response:
        prep = "to" if action == "add" else "from"
        return await ctx.respond(
            "Word ||"
            + str(word)
            + f"|| successfully {action}ed {prep} the swear word list. :tools:",
            ephemeral=True,
        )
    else:
        return await ctx.respond(
            embed=ErrorEmbed(
                f"Could not save the word ||{word}|| to the database. Please contact the administrator or bot developer for further information. "
            ),
            ephemeral=True,
        )


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
                "sqlite3": sqlite3,
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
        title=f"User Muted: {filterMember(member)}",
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
        title=f"User Unmuted: {filterMember(member)}",
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
