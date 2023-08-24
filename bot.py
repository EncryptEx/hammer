import datetime
import json
import os
import sqlite3
import sys
import urllib
from email import message
from os import listdir
from os.path import isfile
from os.path import join
from pydoc import describe
from time import time

import discord
from discord import Embed
from discord import guild_only
from discord.commands import option
from discord.ext import commands
from discord.ext.commands.core import command
from quickchart import QuickChart

from get_enviroment import ANNOUNCEMENTS_CHANNEL
from get_enviroment import COMMAND_PREFIX
from get_enviroment import DEV_SUGGESTIONS_CHANNEL
from get_enviroment import OWNER
from get_enviroment import SECURITY_CHANNEL
from get_enviroment import SECURITY_GUILD
from get_enviroment import SWEAR_WORDS_LIST
from get_enviroment import TOKEN

# Language Loading


def jsonToDict(filename):
    """

    :param filename:

    """
    with open(filename) as f_in:
        return json.load(f_in)


# get all language json files available
langFiles = [f for f in listdir("./langs") if isfile(join("./langs", f))]
languages = dict()
for languageFile in langFiles:
    languages[languageFile.split(".")[0]] = jsonToDict("./langs/" +
                                                       languageFile)

# database import & connection

conn = sqlite3.connect("maindatabase1.db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS `warns` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `userid` INT(100),
        `guildid` INT,
        `reason` TEXT,
        `timestamp` INT);
        """)
cur.execute("""CREATE TABLE IF NOT EXISTS `customWords` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `guildid` INT,
        `uploaderId`INT,
        `word` TEXT,
        `type` INT);
        """)
cur.execute("""CREATE TABLE IF NOT EXISTS `settings` (
        `guildid` INT(100) UNIQUE,
        `automod` INT,
        `language` TEXT);
        """)

hammericon = "https://images-ext-2.discordapp.net/external/OKc8xu6AILGNFY3nSTt7wGbg-Mi1iQZonoLTFg85o-E/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/591633652493058068/e6011129c5169b29ed05a6dc873175cb.png?width=670&height=670"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.AutoShardedBot(command_prefix=COMMAND_PREFIX, intents=intents)
client = discord.Client()

bot.remove_command("help")

#
#   HELP SECTIONN
#


@bot.slash_command(
    name="help", description="Displays all the available commands for Hammer")
async def help(ctx):
    # Define each page

    descr = await GetTranslatedText(ctx.guild.id, "help_description")

    embed = Embed(title="Hammer Bot Help",
                  description=descr,
                  colour=discord.Colour.lighter_grey())

    user = await GetTranslatedText(ctx.guild.id, "user")
    reason = await GetTranslatedText(ctx.guild.id, "reason")
    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "help_moderation_title"),
        value=f"""
    {COMMAND_PREFIX}ban [{user}] <{reason}>
    {COMMAND_PREFIX}kick [{user}] <{reason}>
    {COMMAND_PREFIX}warn [{user}] <{reason}>
    {COMMAND_PREFIX}softwarn [{user}] <{reason}>
    {COMMAND_PREFIX}unwarn [{user}] [id] <{reason}>
    {COMMAND_PREFIX}clearwarns [{user}] <{reason}>
    {COMMAND_PREFIX}seewarns [{user}]
    """,
        inline=True,
    )

    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "help_automod_title"),
        value=await GetTranslatedText(ctx.guild.id,
                                      "help_automod_description",
                                      COMMAND_PREFIX=COMMAND_PREFIX),
        inline=True,
    )

    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "help_chatmod_title"),
        value=await GetTranslatedText(ctx.guild.id,
                                      "help_chatmod_description",
                                      COMMAND_PREFIX=COMMAND_PREFIX),
        inline=True,
    )

    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "help_various_title"),
        value=await GetTranslatedText(ctx.guild.id,
                                      "help_various_description",
                                      COMMAND_PREFIX=COMMAND_PREFIX),
        inline=True,
    )

    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "help_links_title"),
        value=await GetTranslatedText(ctx.guild.id, "help_links_description"),
        inline=True,
    )

    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "help_commands_title"),
        value=await GetTranslatedText(ctx.guild.id,
                                      "help_commands_description",
                                      COMMAND_PREFIX=COMMAND_PREFIX),
        inline=True,
    )

    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
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
    cur.execute("DELETE FROM warns WHERE userid=? AND guildid=?",
                (userid, guildId))
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
        ddt = int(str(dt)[:str(dt).find(".")])
        allwarns.append(
            f"- **ID: {emojis}** Reason: ``{SubReason}``  <t:{ddt}:R>")

        c = c + 1
    return allwarns


async def GetAutomodCustomWords(guildid: int, mode: str):
    wtype = 1 if mode == "allow" else 0
    cur.execute("SELECT word FROM customWords WHERE guildid = ? AND type = ?",
                (guildid, wtype))
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


async def GetSettings(guildid: int, index:int):
    cur.execute("SELECT * FROM settings WHERE guildid = ? LIMIT 1",
                (guildid, ))
    rows = cur.fetchall()
    if len(rows) > 0:
        return rows[0][index]
    else:
        return 0  # default is off


async def GetTranslatedText(guildid: int, index: str, **replace):
    global languages

    dbLanguageRecord = await GetSettings(guildid, 2)
    currentLanguage = "en" if dbLanguageRecord == 0 or dbLanguageRecord == None  else dbLanguageRecord

    text = languages[currentLanguage].get(index, "Word not translated yet.")
    for oldString, newString in replace.items():
        text = text.replace("{" + oldString + "}", str(newString))
    return text


async def SaveSetting(guildid: int, module: str, value: int):
    cur.execute("SELECT * FROM settings WHERE guildid = ? LIMIT 1",
                (guildid, ))
    rows = cur.fetchall()
    # print(rows)
    if len(
            rows
    ) > 0:  # cur.execute('INSERT INTO foo (a,b) values (?,?)', (strA, strB))
        query = f"""UPDATE settings
        SET {module} = {value}
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
            embed=ErrorEmbed(await
                             GetTranslatedText(ctx.guild.id,
                                               "error_deliver_msg",
                                               USERNAME=filterMember(member))),
            ephemeral=True,
        )


# Function to create a template for all errors.
def ErrorEmbed(error):
    """

    :param error:

    """
    embed = Embed(title=f":no_entry_sign: Error!", description=error)

    embed.set_thumbnail(
        url=
        "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ficonsplace.com%2Fwp-content%2Fuploads%2F_icons%2Fff0000%2F256%2Fpng%2Ferror-icon-14-256.png&f=1&nofb=1"
    )

    embed.set_footer(
        text=f"Hammer",
        icon_url=hammericon,
    )
    return embed


def unicodeLetterConver(word):
    """

    :param word:

    """
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
    """

    :param num:

    """
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
    """

    :param member: discord.Member:
    :param member: discord.Member:

    """
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
    settings = await GetSettings(message.guild.id, 1)

    if settings != 1:
        return  # user has disabled Automod or does not have it installed
    words = message.content.split()
    allowed_words_guild_list = await GetAutomodCustomWords(
        message.guild.id, "allow")
    denied_words_guild_list = await GetAutomodCustomWords(
        message.guild.id, "deny")
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
            descr = await GetTranslatedText(
                message.guild.id,
                "automod_warn_description",
                USERNAME=filterMember(member),
            )
            embed = Embed(
                title=await GetTranslatedText(
                    message.guild.id,
                    "automod_warn_title",
                    USERNAME=filterMember(member),
                ),
                description=descr,
            )
            embed.set_footer(
                text=await GetTranslatedText(message.guild.id,
                                             "automod_warn_footer"),
                icon_url=hammericon,
            )
            embed.set_thumbnail(url=member.display_avatar)
            warn = await AddWarning(
                member.id,
                message.guild.id,
                await GetTranslatedText(message.guild.id,
                                        "automod_warn_reason"),
            )
            s = "s" if warn > 1 else ""
            embed.add_field(
                name=await GetTranslatedText(message.guild.id,
                                             "automod_count_title"),
                value=await GetTranslatedText(
                    message.guild.id,
                    "automod_count_description",
                    USERNAME=filterMember(member),
                    WARN=warn,
                    S=s,
                ),
                inline=True,
            )
            bannedmessage = (
                message.content[:message.content.find(originalWord)] + "~~" +
                word + "~~" +
                message.content[message.content.find(originalWord) +
                                len(word):])
            embed.add_field(
                name=await GetTranslatedText(message.guild.id,
                                             "automod_removed_title"),
                value=await GetTranslatedText(
                    message.guild.id,
                    "automod_removed_description",
                    BANNEDMESSAGE=bannedmessage,
                ),
                inline=True,
            )
            embed.add_field(
                name=await GetTranslatedText(message.guild.id,
                                             "automod_nothappy_title"),
                value=await GetTranslatedText(message.guild.id,
                                              "automod_nothappy_description"),
                inline=False,
            )
            await message.channel.send(embed=embed)
            await message.delete()
            try:
                channel = await member.create_dm()
                await channel.send(embed=embed)

            except:
                embed = ErrorEmbed(
                    await message.channel.send(embed=ErrorEmbed(
                        await GetTranslatedText(
                            message.guild.id,
                            "error_deliver_msg",
                            USERNAME=filterMember(member),
                        )), ), )
                message.channel.send(embed=embed)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="you"))
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


debug = True


@bot.slash_command(guild_only=True,
                   name="hello",
                   guild_ids=[int(SECURITY_GUILD)])
async def hello(ctx):
    await ctx.defer()
    text = await GetTranslatedText(ctx.guild.id, "hello_command")
    await ctx.respond(text)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.respond(
            await GetTranslatedText(ctx.guild.id,
                                    "error_404",
                                    ERROR=error,
                                    COMMAND_PREFIX=COMMAND_PREFIX),
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
            await GetTranslatedText(ctx.guild.id, "error_403", FMT=fmt),
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
        descr = await GetTranslatedText(
            ctx.guild.id,
            "whois_description",
            NICK=member.nick,
            USERNAME=username,
            DISCRIMINATOR=discriminator,
            CREATEDAT=member.created_at,
            JOINEDAT=member.joined_at,
            ISBOT=isbot,
            MEMBERID=member.id,
            AVATAR=member.display_avatar,
            TOPROLE=member.top_role,
            WARNS=await GetWarnings(member.id, ctx.guild.id),
        )
        embed = Embed(
            title=await GetTranslatedText(ctx.guild.id,
                                          "whois_title",
                                          MEMBER=filterMember(member)),
            description=descr,
        )

        embed.set_thumbnail(url=member.display_avatar)

        embed.set_footer(
            text=await GetTranslatedText(ctx.guild.id,
                                         "footer_executed_by",
                                         USERNAME=filterMember(ctx.author)),
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
@discord.default_permissions(ban_members=True, )
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.respond(await GetTranslatedText(ctx.guild.id,
                                                  "error_self_ban"),
                          ephemeral=True)
        return
    if reason == None:
        reason = await GetTranslatedText(ctx.guild.id,
                                         "punishment_default_reason")
    message = await GetTranslatedText(ctx.guild.id,
                                      "ban_msg",
                                      GUILD=ctx.guild.name,
                                      REASON=reason)

    descr = await GetTranslatedText(ctx.guild.id,
                                    "ban_description",
                                    MEMBER=filterMember(member),
                                    REASON=reason)
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "ban_title",
                                      MEMBER=filterMember(member)),
        description=descr,
    )
    embed.set_image(url="https://i.imgflip.com/19zat3.jpg")
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    if not debug:
        try:
            await member.ban(reason=reason)
        except:
            ctx.respond(
                embed=ErrorEmbed(await GetTranslatedText(
                    ctx.guild.id,
                    "error_ban_perm",
                    MEMBER=filterMember(member))),
                ephemeral=True,
            )
        return

    embed.set_thumbnail(url=member.display_avatar)
    await ctx.respond(embed=embed)
    await SendMessageTo(ctx, member, message)


@bot.slash_command(guild_only=True,
                   name="kick",
                   description="Kicks out a member from the server")
@discord.default_permissions(kick_members=True, )
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.respond(await GetTranslatedText(ctx.guild.id,
                                                  "error_self_kick"),
                          ephemeral=True)
        return
    if reason == None:
        reason = await GetTranslatedText(ctx.guild.id,
                                         "punishment_default_reason")
    message = await GetTranslatedText(ctx.guild.id,
                                      "kick_msg",
                                      GUILD=ctx.guild.name,
                                      REASON=reason)
    if not debug:
        try:
            await member.kick(reason=reason)
        except:
            ctx.respond(
                embed=ErrorEmbed(await GetTranslatedText(
                    ctx.guild.id,
                    "error_kick_perm",
                    MEMBER=filterMember(member))),
                ephemeral=True,
            )
            return
    descr = await GetTranslatedText(ctx.guild.id,
                                    "kick_description",
                                    MEMBER=filterMember(member),
                                    REASON=reason)
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "kick_title",
                                      MEMBER=filterMember(member)),
        description=descr,
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
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
@discord.default_permissions(administrator=True, )
async def warn(ctx,
               member: discord.Member,
               reason=None,
               softwarn: bool = False):
    if member == ctx.author:
        await ctx.respond(await GetTranslatedText(ctx.guild.id,
                                                  "error_self_warn"),
                          ephemeral=True)
        return
    if reason == None:
        reason = await GetTranslatedText(ctx.guild.id,
                                         "punishment_default_reason")

    message = await GetTranslatedText(ctx.guild.id, "warn_msg", REASON=reason)

    descr = await GetTranslatedText(ctx.guild.id,
                                    "warn_description",
                                    MEMBER=filterMember(member),
                                    REASON=reason)
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "warn_title",
                                      MEMBER=filterMember(member)),
        description=descr,
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await AddWarning(member.id, ctx.guild.id, reason)
    s = "s" if warn > 1 else ""
    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "automod_count_title"),
        value=await GetTranslatedText(
            ctx.guild.id,
            "automod_count_description",
            USERNAME=filterMember(member),
            WARN=warn,
            S=s,
        ),
        inline=True,
    )
    await ctx.respond(embed=embed, ephemeral=softwarn)

    if not softwarn:
        await SendMessageTo(ctx, member, message)


@bot.slash_command(
    guild_only=True,
    name="softwarn",
    description=
    "Sets a silent warning for a user, at 3 warns/strikes they get kicked",
)
@discord.default_permissions(administrator=True, )
async def softwarn(ctx, member: discord.Member, reason=None):
    await warn(ctx, member, reason, True)


@bot.slash_command(
    guild_only=True,
    name="seewarns",
    description="Displays the warn history of a user in the guild",
)
@discord.default_permissions(administrator=True, )
async def seewarns(ctx, member: discord.Member):
    allwarns = await getAllWarns(member.id, ctx.guild.id)
    if len(allwarns) == 0:
        allwarns = [await GetTranslatedText(ctx.guild.id, "warn_no_warns")]
    message = "\n".join(allwarns)

    c = 0
    data = []
    # Data preparation using chart's syntax
    for warn in await GetWarnings(member.id, ctx.guild.id, fullData=True):
        _, _, _, _, timestamp = warn
        c = c + 1
        data.append({
            "t":
            str(
                datetime.datetime.fromtimestamp(
                    int(str(timestamp)[:str(timestamp).find(".")]))),
            "y":
            c,
        })

    qc = QuickChart()
    qc.width = 500
    qc.height = 300
    qc.device_pixel_ratio = 2.0
    qc.config = {
        "type": "line",
        "data": {
            "datasets": [{
                "fill": False,
                "label": [f"Warns of {filterMember(member)}"],
                "lineTension": 0,
                "backgroundColor": "#7289DA",
                "borderColor": "#7289DA",
                "data": data,
            }]
        },
        "options": {
            "scales": {
                "xAxes": [{
                    "type": "time",
                    "time": {
                        "parser": "YYYY-MM-DD HH:mm:ss",
                        "displayFormats": {
                            "day": "DD/MM/YYYY"
                        },
                    },
                }]
            }
        },
    }

    uurl = qc.get_url()

    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "seewarns_title",
                                      MEMBER=filterMember(member)),
        description=message,
    )
    embed.set_image(url=uurl)
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    return await ctx.respond(embed=embed)


@bot.slash_command(guild_only=True,
                   name="unwarn",
                   description="Removes a strike from a user")
@discord.default_permissions(kick_members=True, )
async def unwarn(ctx, member: discord.Member, id: int = None, *, reason=None):
    if await GetWarnings(member.id, ctx.guild.id) == 0:
        return await ctx.respond(await
                                 GetTranslatedText(ctx.guild.id,
                                                   "unwarn_no_warns"))
    if id == None:
        descriptionMsg = await GetTranslatedText(ctx.guild.id,
                                                 "unwarn_description_msg")

        embed = Embed(
            title=await GetTranslatedText(ctx.guild.id,
                                          "unwarn_wrong_selection"),
            description=descriptionMsg,
        )
        allwarns = await getAllWarns(member.id, ctx.guild.id)
        embed.add_field(
            name=await GetTranslatedText(ctx.guild.id,
                                         "seewarns_title",
                                         MEMBER=filterMember(member)),
            value="\n".join(allwarns),
        )
        return await ctx.respond(embed=embed)
    if reason == None:
        reason = await GetTranslatedText(ctx.guild.id,
                                         "unpunishment_default_reason")
    message = await GetTranslatedText(ctx.guild.id,
                                      "unwarn_msg",
                                      REASON=reason)

    descr = await GetTranslatedText(ctx.guild.id,
                                    "unwarn_description",
                                    MEMBER=filterMember(member),
                                    REASON=reason)
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "unwarn_title",
                                      MEMBER=filterMember(member)),
        description=descr,
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await Removewarn(member.id, ctx.guild.id, id)
    s = "s" if warn != 1 else ""
    congrats = "Yey! :tada:" if warn == 0 else ""
    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "automod_count_title"),
        value=await GetTranslatedText(
            ctx.guild.id,
            "unwarn_count_with_success",
            MEMBER=filterMember(member),
            WARN=warn,
            S=s,
            CONGRATS=congrats,
        ),
        inline=True,
    )
    await ctx.respond(embed=embed)
    await SendMessageTo(ctx, member, message)


@bot.slash_command(guild_only=True,
                   name="clearwarns",
                   description="Removes all strikes from a user")
@discord.default_permissions(kick_members=True, )
async def clearwarns(ctx, member: discord.Member, *, reason=None):
    if reason == None:
        reason = await GetTranslatedText(ctx.guild.id,
                                         "unpunishment_default_reason")
    message = await GetTranslatedText(ctx.guild.id,
                                      "clearwarns_msg",
                                      REASON=reason)

    descr = await GetTranslatedText(
        ctx.guild.id,
        "clearwarns_description",
        MEMBER=filterMember(member),
        REASON=reason,
    )
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "clearwarns_title",
                                      MEMBER=filterMember(member)),
        description=descr,
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    embed.set_thumbnail(url=member.display_avatar)
    warn = await Clearwarns(member.id, ctx.guild.id)
    embed.add_field(
        name="Warn count",
        value=await GetTranslatedText(
            ctx.guild.id,
            "unwarn_count_with_success",
            MEMBER=filterMember(member),
            WARN=0,
            S="s",
            CONGRATS="Yey! :tada:",
        ),
        inline=True,
    )
    await ctx.respond(embed=embed, ephemeral=False)
    await SendMessageTo(ctx, member, message)


@bot.slash_command(
    guild_only=True,
    name="automod",
    description="Customizes in this guild Hammer's automod",
)
@discord.default_permissions(administrator=True, )
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
            embed=ErrorEmbed(await GetTranslatedText(ctx.guild.id,
                                                     "error_automod_syntax")),
            ephemeral=True,
        )
    if response:
        prep = "to" if action == "add" else "from"
        return await ctx.respond(
            await GetTranslatedText(
                ctx.guild.id,
                "automod_success_action",
                WORD=str(word),
                ACTION=action,
                PREP=prep,
            ),
            ephemeral=True,
        )
    else:
        return await ctx.respond(
            embed=ErrorEmbed(await GetTranslatedText(ctx.guild.id,
                                                     "error_automod",
                                                     WORD=word)),
            ephemeral=True,
        )


@bot.slash_command(guild_only=True, guild_ids=[int(SECURITY_GUILD)])
async def evaluate(ctx, code):
    if str(ctx.author.id) == str(OWNER):
        try:
            # await respondNotifOwner(
            #     f"User {filterMember(ctx.author)} used command evaluate | id {ctx.author.id}"
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
    """ """
    os.execv(sys.executable, ["python"] + sys.argv)


@bot.slash_command(guild_only=True, guild_ids=[int(SECURITY_GUILD)])
async def restart(ctx):
    if str(ctx.author.id) == str(OWNER):
        try:
            # await respondNotifOwner(
            #     f"User {filterMember(ctx.author)} used command evaluate | id {ctx.author.id}"
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
    description=
    "Updates the message delay in a channel with a set of custom time interval",
)
@discord.default_permissions(manage_messages=True, )
async def setdelay(ctx, seconds: float, reason: str = ""):
    m = (await GetTranslatedText(ctx.guild.id, "modified") if seconds > 0.0
         else await GetTranslatedText(ctx.guild.id, "removed"))
    reason = "for " + reason if reason != "" and reason != None else ""
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "setdelay_title",
                                      M=m,
                                      CHANNEL=ctx.channel),
        description=await GetTranslatedText(ctx.guild.id,
                                            "setdelay_description",
                                            SECONDS=seconds,
                                            REASON=reason),
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
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
@discord.default_permissions(manage_messages=True, )
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
        reason = await GetTranslatedText(ctx.guild.id,
                                         "punishment_default_reason")

    embed = discord.Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "mute_title",
                                      MEMBER=filterMember(member)),
        description=await GetTranslatedText(ctx.guild.id,
                                            "mute_description",
                                            MENTION=member.mention,
                                            REASON=reason),
        colour=discord.Colour.red(),
    )
    await ctx.respond(embed=embed)
    await member.add_roles(mutedRole, reason=reason)

    SendMessageTo(
        ctx,
        member,
        await GetTranslatedText(ctx.guild.id,
                                "mute_msg",
                                GUILD=ctx.guild.name,
                                REASON=reason),
    )


# description="Unmutes a specified user."
@bot.slash_command(
    guild_only=True,
    name="unmute",
    description=
    "Restores the hability to talk or join voice channels to a user",
)
@discord.default_permissions(manage_messages=True, )
async def unmute(ctx, member: discord.Member, *, reason=None):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    if reason == None:
        reason = ""
    else:
        reason = "for " + reason
    await member.remove_roles(mutedRole)
    SendMessageTo(
        ctx,
        member,
        await GetTranslatedText(ctx.guild.id,
                                "unmute_msg",
                                GUILD=ctx.guild.name,
                                REASON=reason),
    )
    embed = discord.Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "unmute_title",
                                      MEMBER=filterMember(member)),
        description=await GetTranslatedText(ctx.guild.id,
                                            "unmute_description",
                                            MENTION=member.mention,
                                            REASON=reason),
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
        title=await GetTranslatedText(ctx.guild.id,
                                      "lock_title",
                                      CHANNEL=ctx.channel),
        description=await GetTranslatedText(ctx.guild.id,
                                            "lock_description",
                                            REASON=reason),
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    await ctx.respond(embed=embed)


@discord.default_permissions(manage_channels=True)
@bot.slash_command(
    guild_only=True,
    name="unlock",
    description=
    "Removes the blocking in a channel from not being used as a chat.",
)
async def unlock(ctx, channel: discord.TextChannel = None, reason=None):
    channel = channel or ctx.channel
    reason = "for " + reason if reason else ""
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id,
                                      "unlock_title",
                                      CHANNEL=ctx.channel),
        description=await GetTranslatedText(ctx.guild.id,
                                            "unlock_description",
                                            REASON=reason),
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    await ctx.respond(embed=embed)


@bot.slash_command(
    name="suggest",
    description="Sends a suggestion to the developer of Hammer.",
)
async def suggest(ctx, suggestion: str):
    embed = Embed(
        title=
        f"The user {filterMember(ctx.author)} has posted a suggestion! :hammer_pick:",
        description=f"{suggestion}",
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    suggestionChannel = bot.get_channel(int(DEV_SUGGESTIONS_CHANNEL))
    await suggestionChannel.send(embed=embed)
    await ctx.respond(
        await GetTranslatedText(ctx.guild.id, "suggest_success"),
        ephemeral=True,
    )


@bot.slash_command(
    name="invite",
    description="Returns the bot's invitation link.",
)
async def invite(ctx):
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id, "hammer_invite"),
        description=
        f"[**🔗{await GetTranslatedText(ctx.guild.id, 'hammer_link')}**](https://discordapp.com/api/oauth2/authorize?client_id=591633652493058068&permissions=8&scope=bot)",
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    await ctx.respond(embed=embed)


modules = ["automod", "language"]


@discord.default_permissions(administrator=True)
@bot.slash_command(name="settings",
                   description="Modifies some Hammer config values",
                   guild_only=True)
@option(
    "module",
    description="Pick a module to switch!",
    autocomplete=discord.utils.basic_autocomplete(modules),
)
@option(
    "value",
    description="Select on/off",
    autocomplete=discord.utils.basic_autocomplete(["on", "off", [k for k,v in languages.items()]]),
)
async def settings(ctx, module: str = None, value: str = None):
    if module != None and value != None:
        if module in modules:
            if module=="automod":
                value = 1 if value == "on" else 0
                await SaveSetting(ctx.guild.id, module, value)
                action = "enabled" if value else "disabled"
                await ctx.respond(
                    await GetTranslatedText(ctx.guild.id,
                                            "settings_module",
                                            MODULE=module,
                                            ACTION=action),
                    ephemeral=True,
                )
                
            elif module=="language": 
                languagesOptions = [k for k,v in languages.items()]
                if(value in languagesOptions):
                    await SaveSetting(ctx.guild.id, module, value)
                    action = "set to " + value
                    await ctx.respond(
                        await GetTranslatedText(ctx.guild.id,
                                                "settings_module",
                                                MODULE=module,
                                                ACTION=action),
                        ephemeral=True,
                    )
                else: 
                    await ctx.respond(
                        await GetTranslatedText(ctx.guild.id, "error_settings_syntax", COMMAND="/settings language "+'/'.join(languagesOptions)),
                    ephemeral=True)
                
            else:
                await ctx.respond(
                    await GetTranslatedText(ctx.guild.id, "error_settings_syntax", COMMAND="/settings automod on/off"),
                    ephemeral=True,
                )
                return
            
        else:
            await ctx.respond(
                await GetTranslatedText(ctx.guild.id, "error_settings_syntax", COMMAND="/settings module value"),
                ephemeral=True,
            )
            return
    embed = Embed(
        title=await GetTranslatedText(ctx.guild.id, "settings_title"),
        description=await GetTranslatedText(ctx.guild.id,
                                            "settings_description"),
    )
    print("getting settings from discord.Guild.id", ctx.guild.id)
    automodStatus = await GetSettings(ctx.guild.id, 1)
    automodStatustr = "**✅ ON**" if automodStatus else "**❌ OFF**"
    recommendedactivityAutomod = (
        await GetTranslatedText(ctx.guild.id,
                                "settings_disable_automod",
                                COMMAND_PREFIX=COMMAND_PREFIX) if automodStatus
        else await GetTranslatedText(ctx.guild.id,
                                     "settings_enable_automod",
                                     COMMAND_PREFIX=COMMAND_PREFIX))
    embed.add_field(
        name=await GetTranslatedText(ctx.guild.id, "help_automod_title"),
        value=await GetTranslatedText(
            ctx.guild.id,
            "automod_status",
            STATUS=automodStatustr,
            RECOMMENDED=recommendedactivityAutomod,
        ),
        inline=True,
    )
    embed.set_footer(
        text=await GetTranslatedText(ctx.guild.id,
                                     "footer_executed_by",
                                     USERNAME=filterMember(ctx.author)),
        icon_url=hammericon,
    )
    await ctx.respond(embed=embed)


bot.run(TOKEN)
