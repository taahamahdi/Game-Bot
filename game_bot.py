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

base_url = "http://store.steampowered.com/search/suggest"
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


#
# This code is from Hugop#2950 on the "Discord Bot List" server
# This code provides provides the number of servers Game-Bot is running on for
# DiscordBots.org's API.
#
# Some of this code has already been merged in with:
# * on_ready()
#
dbltoken = "TOKEN"
# Replace "TOKEN" with your DiscordBots.org API token

url = "https://discordbots.org/api/bots/" + client.bot.id + "/stats"
headers = {"Authorization": dbltoken}

# This was merged into the existing on_ready() function
# async def on_ready():
#     payload = {"server_count"  : len(bot.servers)}
#     async with aiohttp.ClientSession() as aioclient:
#             await aioclient.post(url, data=payload, headers=headers)


#
# on_server_join(server) and on_server_remove(server) keep a count of
# how many servers Game-Bot is on.
#

async def on_server_join(server):
    payload = {"server_count": len(client.servers)}
    async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(url, data=payload, headers=headers)


async def on_server_remove(server):
    payload = {"server_count": len(client.servers)}
    async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(url, data=payload, headers=headers)
#
# end of Hugop's code
#


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
    app_id = appid_regex.search(img_url)[1]
    logger.debug("Returning appid %s" % app_id)
    return app_id


@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('------')  # To show that the bot can log in
    await client.change_presence(game=discord.Game(name='!game help'))

    # Code from Hugop (see above)
    payload = {"server_count": len(client.servers)}
    async with aiohttp.ClientSession() as aioclient:
        await aioclient.post(url, data=payload, headers=headers)
    # End of Hugop's code



#creating game command group
@client.group(pass_context=True)
async def game(ctx):
    if ctx.invoked_subcommand is None:
        game_name = ctx.message.content[6:]
        if game_name.lower() == "csgo" \
            or game_name.lower() == "cs" \
                or game_name.lower() == "cs:go":
            # To bypass API shortcomings for popular games

            await client.send_message(
                ctx.message.channel,
                "http://store.steampowered.com/app/730")

        elif game_name.lower() == "pubg":

            await client.send_message(
                ctx.message.channel,
                "http://store.steampowered.com/app/578080")

        elif game_name.lower() == "n++":

            await client.send_message(
                ctx.message.channel,
                "http://store.steampowered.com/app/230270")

        elif game_name.lower() == "gta"     \
            or game_name.lower() == "gta5"  \
            or game_name.lower() == "gtav"  \
            or game_name.lower() == "gta 5" \
                or game_name.lower() == "gta v":

            await client.send_message(
                ctx.message.channel,
                "http://store.steampowered.com/app/271590")

        elif game_name.lower() == "tf2":

            await client.send_message(
                ctx.message.channel,
                "http://store.steampowered.com/app/440")

        elif len(game_name) > 0:
            try:
                app_id = game_search(game_name)
                if app_id:
                    await client.send_message(
                        ctx.message.channel,
                        "http://store.steampowered.com/app/" + app_id)
                else:
                    await client.send_message(
                        ctx.message.channel,
                        ("Please try again with less characters, "
                         "the game's full name, or with a different game.")
                        )

            except urllib.error.HTTPError as e:
                code = e.code
                logger.error("Got HTTPError %s" % code)
                await client.send_message(
                    ctx.message.channel, "Error {} returned :(".format(code)
                )
            except Exception as e:
                logger.exception("Exception in game searching")
                await client.send_message(
                    ctx.message.channel, "Exception :("
                )

        else:
            await client.send_message(
                ctx.message.channel,
                "Please enter your search term!")

#help subcommand, describes usage for !game
@game.command(pass_context=True)
async def help(ctx):
    await client.send_message(
        ctx.message.channel,
        ("Simply type **!game followed by the game "
         "you wished to be linked to** on Steam!\n\n"

         "Use **!game bugs** to get a link to a Discord server "
         "where you can report bugs.\n\n"

         "Use **!game donate** for an ETH address to "
         "help pay server hosting fees.\n\n"
         "Use **!game info** to find out more about how the bot works!")
        )


#info subcommand, gives info about bot creator
@game.command(pass_context=True)
async def info(ctx):
    await client.send_message(
        ctx.message.channel,
        ("Game-Bot is written in Python, using Discord.py as an API "
         "wrapper for Discord. "
         "The bot was coded by <@156971607057760256>, a student at the "
         "University of Waterloo in Canada.")
        )

    await client.send_message(
        ctx.message.channel,
        ("You can take a look at the code at:\n"
         "https://github.com/taahamahdi/Game-Bot")
        )


#bugs subcommand, links server for bug reports
@game.command(pass_context=True)
async def bugs(ctx):
    await client.send_message(
        ctx.message.channel,
        ("Please join https://discord.gg/AZTP5fK with all "
         "your bugs (and to talk with me, Cool :])")
        )


#donate subcommand, gives donation link
@game.command(pass_context=True)
async def donate(ctx):
    await client.send_message(
        ctx.message.channel,
        ("All money goes directly to server hosting and bot development, "
          "not to me (or anyone else).")
        )
    await client.send_message(
        ctx.message.channel,
        "ETH: **0x8E48AD118491C571a5E22E990cea4A9d099cDEDc**")
    await client.send_message(
        ctx.message.channel,
        "Other forms of donations coming soon!")
    




if __name__ == "__main__":
    token = os.environ.get("GAME_BOT_TOKEN")
    if not token:
        print("Set GAME_BOT_TOKEN as an env var with your token")
    else:
        client.run(token)
