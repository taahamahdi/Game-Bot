import discord
import logging
import os
import re
import urllib.request
import urllib.parse
import aiohttp

from discord.ext.commands import Bot
from lxml import html

#
# Game-Bot.py contains some functions based
#   on Rapptz's Discord.py's bot examples
#
#   https://github.com/Rapptz/discord.py
#

# os.environ["GAME_BOT_TOKEN"] = "TOKEN"
# [Optional] Set your Bot token directly through the code

base_url = "https://store.steampowered.com/search/suggest"
appid_regex = re.compile("steam/apps/([0-9]+)/")

client = Bot(command_prefix='!')  # Creating bot instance

logger = logging.getLogger('game_bot')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='game_bot.log',
    encoding='utf-8',
    mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client.remove_command('help')
# Prevents bot from responding to !help calls

game_exceptions = {
    "csgo": "https://store.steampowered.com/app/730",
    "cs": "https://store.steampowered.com/app/730",
    "cs:go": "https://store.steampowered.com/app/730",
    "pubg": "https://store.steampowered.com/app/578080",
    "n++": "https://store.steampowered.com/app/230270",
    "gta": "https://store.steampowered.com/app/271590",
    "gta5": "https://store.steampowered.com/app/271590",
    "gtav": "https://store.steampowered.com/app/271590",
    "gta 5": "https://store.steampowered.com/app/271590",
    "gta v": "https://store.steampowered.com/app/271590",
    "tf2": "https://store.steampowered.com/app/440",
    "fortnite": "https://www.epicgames.com/fortnite",
    "overwatch": "https://playoverwatch.com",
    "hearthstone": "https://playhearthstone.com",
    "league of legends": "https://leagueoflegends.com",
    "lol": "https://leagueoflegends.com",
    "osu": "https://osu.ppy.sh",
    "osu!": "https://osu.ppy.sh",
    "roblox": "https://roblox.com"
}

# This code is from Hugop#2950 on the "Discord Bot List" server
# This code provides provides the number of servers Game-Bot is
# running on for DiscordBots.org's API.
dbltoken = None
# Replace with your DiscordBots.org API token


async def dbl_post(payload, bot_id):
    if dbltoken:
        url = "https://discordbots.org/api/bots/" + bot_id + "/stats"
        headers = {"Authorization": dbltoken}
        async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(url, data=payload, headers=headers)


# on_server_join(server) and on_server_remove(server) keep a count of
# how many servers Game-Bot is on.
async def on_server_join(server):
    payload = {"server_count": len(client.servers)}
    await dbl_post(payload, client.user.id)

async def on_server_remove(server):
    payload = {"server_count": len(client.servers)}
    await dbl_post(payload, client.user.id)

# end of Hugop's code

@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='!game help'))

    payload = {"server_count": len(client.servers)}

    await dbl_post(payload, client.user.id)


def game_search(name):
    """Search for a game with the given name.

    Returns None if no results were found;
    otherwise returns the appid as a string
    """
    logger.info("Searching for %s" % name)
    data = urllib.parse.urlencode({'term': name, 'f': 'games'})
    data = data.encode('utf-8')
    with urllib.request.urlopen(base_url, data) as f:
        resp = f.read()
    if not resp:
        logger.info("Received empty response for %s" % name)
        return None

    tree = html.fromstring(resp)
    img_url = tree.xpath('//img[position() = 1]')[0].get("src")
    app_id = appid_regex.search(img_url).group(1)
    logger.debug("Returning appid %s" % app_id)
    return app_id


# creating game command group
@client.group(pass_context=True)
async def game(ctx):
    if ctx.invoked_subcommand is None:
        await client.send_typing(ctx.message.channel)
        game_name = ctx.message.content[6:]
        if game_name.lower() in game_exceptions:
            await client.send_message(
                ctx.message.channel,
                game_exceptions[game_name.lower()])
        elif len(game_name) > 0:
            try:
                app_id = game_search(game_name)
                if app_id:
                    await client.send_message(
                        ctx.message.channel,
                        "https://store.steampowered.com/app/" + app_id)
                else:
                    await client.send_message(
                        ctx.message.channel,
                        ("Please try again with fewer characters, "
                         "the game's full name, or with a different game.")
                    )
                    await client.add_reaction(ctx.message, "\U0001F622")

            except urllib.error.HTTPError as e:
                code = e.code
                logger.error("Got HTTPError %s" % code)
                await client.send_message(
                    ctx.message.channel, "Error {} returned :[".format(code)
                )
            except Exception as e:
                logger.exception("Exception in game searching")
                await client.send_message(
                    ctx.message.channel, "Exception :["
                )
                await client.add_reaction(ctx.message, "\U0001F62D")

        else:
            await client.send_message(
                ctx.message.channel,
                "Please enter your search term!")


# help subcommand, describes usage for !game
@game.command(pass_context=True)
async def help(ctx):
    await client.send_typing(ctx.message.channel)
    await client.send_message(
        ctx.message.channel,
        ("Simply type **!game followed by the game "
         "you wished to be linked to** on Steam.\n"
         "Use **!game bugs** to get a link to a Discord server "
         "where you can report bugs.\n"
         "Use **!game donate** for an ETH address to "
         "help pay server hosting fees.\n"
         "Use **!game info** to find out more about how the bot works!\n"
         "Add a backslash to find a game that starts with \"bugs,\""
         " \"donate,\" or \"info.\"")
    )


# info subcommand, gives info about bot creator
@game.command(pass_context=True)
async def info(ctx):
    await client.send_typing(ctx.message.channel)
    await client.send_message(
        ctx.message.channel,
        ("Game-Bot is written in Python, using Discord.py as an API "
         "wrapper for Discord. "
         "The bot was coded by <@156971607057760256>, a student at the "
         "University of Waterloo in Canada.")
    )
    await client.send_typing(ctx.message.channel)
    await client.send_message(
        ctx.message.channel,
        ("You can take a look at the code at:\n"
         "https://github.com/taahamahdi/Game-Bot")
    )


# bugs subcommand, links server for bug reports
@game.command(pass_context=True)
async def bugs(ctx):
    await client.send_typing(ctx.message.channel)
    await client.send_message(
        ctx.message.channel,
        ("Please join https://discord.gg/AZTP5fK with all "
         "your bugs (and to talk with me, <@156971607057760256> :])")
    )


# donate subcommand, gives donation link
@game.command(pass_context=True)
async def donate(ctx):
    await client.send_typing(ctx.message.channel)
    await client.send_message(
        ctx.message.channel,
        "All money goes directly to server hosting fees."
    )
    await client.send_typing(ctx.message.channel)
    await client.send_message(
        ctx.message.channel,
        "**ETH**: 0x8E48AD118491C571a5E22E990cea4A9d099cDEDc"
    )

if __name__ == "__main__":
    token = os.environ.get("GAME_BOT_TOKEN")
    if not token:
        print("Set GAME_BOT_TOKEN as an env var with your token")
    else:
        client.run(token)
