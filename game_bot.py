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
    print("Guild count: %s" % len(client.guilds))
    print("------")
    await client.change_presence(activity=discord.Game(name='!game help'))
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
    app_id_search = APPID_REGEX.search(img_url)
    if not app_id_search:
        logger.info("Regular expression returned NoneType for %s" % name)
        return None

    app_id = app_id_search.group(1)
    logger.debug("Returning appid %s" % app_id)
    return app_id


# creating game command group
@client.group()
async def game(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.trigger_typing()

        # Keep count of calls to !game
        increment_count('total_game_count', user_preferences_dict)

        game_name = ctx.message.content[6:]
        if game_name.lower() in game_exceptions:
            if "steampowered" in game_exceptions[game_name.lower()]:
                await ctx.send(embed=game_message(
                    re.findall("\d+",
                               game_exceptions[game_name.lower()])[0],
                    ctx))
            else:
                await ctx.send(game_exceptions[game_name.lower()])
        elif len(game_name) > 0:
            try:
                if int(ctx.guild.id) in user_preferences_dict:
                    country = user_preferences_dict[int(ctx.guild.id)]
                    app_id = game_search(game_name, country)
                else:
                    app_id = game_search(game_name)

                if app_id:
                    embed = game_message(app_id, ctx)
                    if embed:
                        await ctx.send(embed=embed)
                    else:
                        await ctx.channel.send(STORE_BASE_URL + app_id)
                else:
                    await ctx.channel.send(INVALID_GAME_NAME)
                    await ctx.message.add_reaction(CRY_EMOJI)

            except urllib.error.HTTPError as e:
                code = e.code
                logger.error("Got HTTPError %s" % code)
                await ctx.channel.send("Error {} returned :[".format(code))
                await ctx.channel.send("Please report this bug in %s." % HELP_URL)
                await ctx.channel.send("Here's the error:")
                await ctx.channel.send(code_format("%s" % e))
                await ctx.message.add_reaction(SOB_EMOJI)
            except Exception as e:
                logger.exception("Exception in game searching %s" % e)
                await ctx.channel.send("Exception :[")
                await ctx.channel.send("Please report this bug in %s." % HELP_URL)
                await ctx.channel.send("Here's the error:")
                await ctx.channel.send(code_format("%s" % e))
                await ctx.message.add_reaction(SOB_EMOJI)

        else:
            await ctx.channel.send("Please enter your search term.")


# help subcommand, describes usage for !game
@game.command()
async def help(ctx):
    await ctx.trigger_typing()
    await ctx.send(embed=HELP_EMBED)


# stats subcommand, gives bot usage info
@game.command()
async def stats(ctx):
    await ctx.trigger_typing()
    cpu_usage = psutil.cpu_percent()
    mem_usage = dict(psutil.virtual_memory()._asdict())['percent']
    stats_embed = get_stats_embed(cpu_usage,
                                  mem_usage,
                                  len(client.guilds),
                                  user_preferences_dict['total_game_count'])
    await ctx.send(embed=stats_embed)


# source subcommand, gives source code/creator info
@game.command()
async def source(ctx):
    await ctx.trigger_typing()
    await ctx.channel.send(SOURCE_INFO)
    await ctx.trigger_typing()
    await ctx.channel.send(
        ("You can take a look at the code at:\n"
         "https://github.com/taahamahdi/Game-Bot")
    )


# bugs subcommand, links guild for bug reports
@game.command()
async def bugs(ctx):
    await ctx.trigger_typing()
    await ctx.channel.send(
        ("Please join %s with all your bugs (and to talk with me, "
         "<@156971607057760256> :])" % HELP_URL))


# country subcommand, store the user's country preferences in another file
@game.command()
async def country(ctx):
    await ctx.trigger_typing()
    country = ctx.message.content[14:]
    guild_id = ctx.guild.id
    if len(country) == 2:
        user_preferences_dict[guild_id] = country
        await ctx.channel.send(
            "Country set to %s." % code_format(country))
    else:
        await ctx.channel.send(
            ("Invalid country code. Consult this list to find your country "
             "code:\nhttps://laendercode.net/en/2-letter-list.html"))


# TODO: Implement daily/monthly usage counters
def increment_count(dict_key, dictionary):
    if dict_key in dictionary:
        dictionary[dict_key] += 1
    else:
        dictionary[dict_key] = 0


def code_format(item):
    """ Surrounds given item with '`', which will make it appear as code in
    Discord chat."""
    return "`%s`" % item


if __name__ == "__main__":
    token = os.environ.get("GAME_BOT_TOKEN")
    if not token:
        print("Set GAME_BOT_TOKEN as an environment variable with your token")
    else:
        client.run(token)
