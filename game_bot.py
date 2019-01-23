import discord
import logging
import os
import re
import urllib.request
import urllib.parse
import psutil

from discord.ext.commands import Bot
from discord.ext.commands import CommandNotFound
from lxml import html

import dbl_tracker

from constants import SEARCH_SUGGEST_URL
from constants import STORE_BASE_URL
from constants import APPID_REGEX
from constants import INVALID_GAME_NAME
from constants import SOURCE_INFO
from constants import CRY_EMOJI
from constants import SOB_EMOJI
from constants import HELP_URL

from constants import game_exceptions
from constants import user_preferences_dict

from embed import HELP_EMBED
from embed import get_stats_embed
from embed import game_message


# [Optional] Set your Bot token directly through the code
# os.environ["GAME_BOT_TOKEN"] = "TOKEN"

client = Bot(command_prefix='!')  # Creating bot instance

# Prevents bot from responding to !help calls
client.remove_command('help')

# Logging setup
logger = logging.getLogger('game_bot')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='bot.log',
    encoding='utf-8',
    mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)
    print("Server count: %s" % len(client.servers))
    print("------")
    await client.change_presence(game=discord.Game(name='!game help'))
    dbl_tracker.setup(client)


# Handle CommandNotFound Exception
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return


def game_search(name, country="us"):
    """Search for a game with the given name.

    Returns None if no results were found;
    otherwise returns the appid as a string
    """
    logger.info("Searching for %s" % name)
    data = urllib.parse.urlencode({'term': name,
                                   'f': 'games',
                                   'cc': country})
    data = data.encode('utf-8')
    with urllib.request.urlopen(SEARCH_SUGGEST_URL, data) as f:
        resp = f.read()
    if not resp:
        logger.info("Received empty response for %s" % name)
        return None

    tree = html.fromstring(resp)
    img_url = tree.xpath('//img[position() = 1]')[0].get("src")
    app_id = APPID_REGEX.search(img_url).group(1)
    logger.debug("Returning appid %s" % app_id)
    return app_id


# TODO: Implement daily/monthly usage counters
def increment_count(dict_key, dictionary):
    if dict_key in dictionary:
        dictionary[dict_key] += 1
    else:
        dictionary[dict_key] = 0


# creating game command group
@client.group(pass_context=True)
async def game(ctx):
    if ctx.invoked_subcommand is None:
        await client.send_typing(ctx.message.channel)

        # Keep count of calls to !game
        increment_count('total_game_count', user_preferences_dict)

        game_name = ctx.message.content[6:]
        if game_name.lower() in game_exceptions:
            if "steampowered" in game_exceptions[game_name.lower()]:
                await client.say(embed=game_message(
                    re.findall("\d+",
                               game_exceptions[game_name.lower()])[0],
                    ctx))
            else:
                await client.send_message(ctx.message.channel,
                                          game_exceptions[game_name.lower()])
        elif len(game_name) > 0:
            try:
                if int(ctx.message.server.id) in user_preferences_dict:
                    country = user_preferences_dict[int(ctx.message.server.id)]
                    app_id = game_search(game_name, country)
                else:
                    app_id = game_search(game_name)

                if app_id:
                    embed = game_message(app_id, ctx)
                    if embed:
                        await client.say(embed=game_message(app_id, ctx))
                    else:
                        await client.send_message(ctx.message.channel,
                                                  STORE_BASE_URL + app_id)
                else:
                    await client.send_message(ctx.message.channel,
                                              INVALID_GAME_NAME)
                    await client.add_reaction(ctx.message, CRY_EMOJI)

            except urllib.error.HTTPError as e:
                code = e.code
                logger.error("Got HTTPError %s" % code)
                await client.send_message(ctx.message.channel,
                                          "Error {} returned :[".format(code))
                await client.send_message(ctx.message.channel,
                                          "Please report this bug in %s."
                                          % HELP_URL)
                await client.add_reaction(ctx.message, SOB_EMOJI)
            except Exception as e:
                logger.exception("Exception in game searching %s" % e)
                await client.send_message(
                    ctx.message.channel, "Exception :["
                )
                await client.send_message(ctx.message.channel,
                                          "Please report this bug in %s."
                                          % HELP_URL)
                await client.add_reaction(ctx.message, SOB_EMOJI)

        else:
            await client.send_message(
                ctx.message.channel,
                "Please enter your search term.")


# help subcommand, describes usage for !game
@game.command(pass_context=True)
async def help(ctx):
    await client.send_typing(ctx.message.channel)
    await client.say(embed=HELP_EMBED)


# stats subcommand, gives bot usage info
@game.command(pass_context=True)
async def stats(ctx):
    await client.send_typing(ctx.message.channel)
    cpu_usage = psutil.cpu_percent()
    mem_usage = dict(psutil.virtual_memory()._asdict())['percent']
    stats_embed = get_stats_embed(cpu_usage,
                                  mem_usage,
                                  len(client.servers),
                                  user_preferences_dict['total_game_count'])
    await client.say(embed=stats_embed)


# source subcommand, gives source code/creator info
@game.command(pass_context=True)
async def source(ctx):
    await client.send_typing(ctx.message.channel)
    await client.send_message(ctx.message.channel, SOURCE_INFO)
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
        ("Please join %s with all your bugs (and to talk with me, "
         "<@156971607057760256> :])" % HELP_URL))


def code_format(item):
    """ Surrounds given item with '`', which will make it appear as code in
    Discord chat."""
    return "`%s`" % item


# country subcommand, store the user's country preferences in another file
@game.command(pass_context=True)
async def country(ctx):
    await client.send_typing(ctx.message.channel)
    country = ctx.message.content[14:]
    server_id = int(ctx.message.server.id)
    if len(country) == 2:
        user_preferences_dict[server_id] = country
        await client.send_message(
            ctx.message.channel,
            "Country set to %s." % code_format(country))
    else:
        await client.send_message(
            ctx.message.channel,
            ("Invalid country code. Consult this list to find your country "
             "code:\nhttps://laendercode.net/en/2-letter-list.html"))


if __name__ == "__main__":
    token = os.environ.get("GAME_BOT_TOKEN")
    if not token:
        print("Set GAME_BOT_TOKEN as an environment variable with your token")
    else:
        client.run(token)
