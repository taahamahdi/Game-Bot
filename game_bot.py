import discord
import logging
import os
import re
import urllib.request
import urllib.parse

from lxml import html

# Game-Bot.py contains some functions based on Rapptz's Discord.py's bot examples
#
#                    https://github.com/Rapptz/discord.py

base_url = "http://store.steampowered.com/search/suggest"
appid_regex = re.compile("steam/apps/([0-9]+)/")

client = discord.Client() # Creating bot instance

logger = logging.getLogger('game_bot')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='game_bot.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


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
    print('------') # To show that the bot can log in
    await client.change_presence(game=discord.Game(name = '!game help'))

@client.event
async def on_message(message):
    if message.content.startswith('!game help'):

        await client.send_message(message.channel, "Simply type !game followed by the game you wished to be linked to on Steam!")
        await client.send_message(message.channel, "Use !game bugs to get a link to a Discord server where you can report bugs.")
        await client.send_message(message.channel, "Use !game donate to get BTC/ETH addresses to help pay server hosting fees.")

    elif message.content.startswith('!game bugs'):

        await client.send_message(message.channel, "Please join https://discord.gg/AZTP5fK with all your bugs (and to talk with me, Cool :])")

    elif message.content.startswith('!game donate'):

        await client.send_message(message.channel, "All money goes directly to server hosting and bot development, not to me or anyone else.")
        await client.send_message(message.channel, "ETH: 0x8E48AD118491C571a5E22E990cea4A9d099cDEDc")
        await client.send_message(message.channel, "Other forms of donations coming soon!")

    elif message.content.startswith('!game'): #When !game is entered in chat
        game_name = message.content[6:]
        if game_name.lower() == "csgo" or game_name.lower() == "cs" or game_name.lower() == "cs:go":
            # To bypass API shortcomings for popular games

            await client.send_message(message.channel, "http://store.steampowered.com/app/730")

        elif game_name.lower() == "pubg":

            await client.send_message(message.channel, "http://store.steampowered.com/app/578080")

        elif game_name.lower() == "n++":

            await client.send_message(message.channel, "http://store.steampowered.com/app/230270")

        elif game_name.lower() == "gta" or game_name.lower() == "gta5" or game_name.lower() == "gtav" \
          or game_name.lower() == "gta 5" or game_name.lower() == "gta v":

            await client.send_message(message.channel, "http://store.steampowered.com/app/271590")

        elif len(game_name) > 0:
            try:
                app_id = game_search(game_name)
                if app_id:
                    await client.send_message(message.channel, "http://store.steampowered.com/app/" + app_id)
                else:
                    await client.send_message(message.channel, "Try again with more characters or a different game!")

            except urllib.error.HTTPError as e:
                code = e.code
                logger.error("Got HTTPError %s" % code)
                await client.send_message(
                    message.channel, "Error {} returned :(".format(code)
                )
            except Exception as e:
                logger.exception("Exception in game searching")
                await client.send_message(
                    message.channel, "Exception :("
                )

        else:
            await client.send_message(message.channel, "Please enter your search term!")


if __name__ == "__main__":
    token = os.environ.get("GAME_BOT_TOKEN")
    if not token:
        print("Set GAME_BOT_TOKEN as an env var with your token")
    else:
        client.run(token)
