import json
import discord
import urllib

from constants import user_preferences_dict
from constants import EMBED_COLOR
from constants import HELP_URL
from constants import HELP_IMAGE
from constants import HELP_COUNTRY_VAL
from constants import HELP_STATS_VAL
from constants import HELP_BUGS_VAL
from constants import HELP_SOURCE_VAL
from constants import HELP_FOOTER


# Embed message for !game help
HELP_EMBED = discord.Embed(title="Command Help", color=EMBED_COLOR)
HELP_EMBED.set_author(name="Game-Bot", url=HELP_URL, icon_url=HELP_IMAGE)
HELP_EMBED.add_field(name="!game [game name]",
                     value="Search for [game name] on Steam.", inline=False)
HELP_EMBED.add_field(name="!game country",
                     value=HELP_COUNTRY_VAL,
                     inline=False)
HELP_EMBED.add_field(name="!game stats",
                     value=HELP_STATS_VAL,
                     inline=False)
HELP_EMBED.add_field(name="!game bugs",
                     value=HELP_BUGS_VAL,
                     inline=False)
HELP_EMBED.add_field(name="!game source",
                     value=HELP_SOURCE_VAL,
                     inline=False)
HELP_EMBED.set_footer(text=HELP_FOOTER)


# Embed message for !game stats
def get_stats_embed(cpu_usage, mem_usage, server_count, searches):
    stats_embed = discord.Embed(title="Bot Statistics", color=EMBED_COLOR)
    stats_embed.set_author(name="Game-Bot", url=HELP_URL, icon_url=HELP_IMAGE)
    stats_embed.add_field(name="CPU Usage",
                          value="%s %%" % cpu_usage, inline=True)
    stats_embed.add_field(name="Memory Usage",
                          value="%s %%" % mem_usage, inline=True)
    stats_embed.add_field(name="Servers",
                          value=server_count, inline=True)
    stats_embed.add_field(name="Searches",
                          value=searches, inline=True)
    return stats_embed


# Embed message for !game
def get_price(data):
    price = data['price_overview']['final_formatted']
    if data['price_overview']['discount_percent'] > 0:
        price += " (%s%% off)" % data['price_overview']['discount_percent']
    return price


def get_release_date(rdate_info):
    if rdate_info['coming_soon']:
        return "Coming soon"
    return rdate_info['date']


def get_genres(genre_info):
    genre_list = []
    for genre in genre_info:
        genre_list.append(genre['description'])
    return '\n'.join(map(str, genre_list))


def get_platforms(platform_info):
    platform_list = []
    for platform in platform_info:
        platform_list.append(platform.title())
    return '\n'.join(map(str, platform_list))


def game_message(app_id, ctx):
    """ Creates and sends an Discord embed message with relevant game
    data.
    """
    server_id = int(ctx.message.server.id)
    if server_id in user_preferences_dict:
        country_code = user_preferences_dict[server_id]
    else:
        country_code = 'us'
    j = urllib.request.urlopen(
        "https://store.steampowered.com/api/appdetails/?appids=%s&cc=%s" %
        (app_id, country_code))
    json_obj = json.load(j)
    if json_obj[app_id]['success']:
        data = json_obj[app_id]['data']

        if data['is_free']:
            price = "Free"
        else:
            price = get_price(data)
        required_age = int(data['required_age'])

        embed = discord.Embed(
            title=data['name'],
            url="https://store.steampowered.com/app/%s" % app_id,
            description=data['short_description'],
            color=EMBED_COLOR)
        embed.add_field(name="Price",
                        value=price,
                        inline=True)
        if 'metacritic' in data:
            embed.add_field(name="Metacritic Score",
                            value=data['metacritic']['score'],
                            inline=True)
        if required_age > 0:
            embed.add_field(name="Required Age",
                            value=required_age,
                            inline=True)
        embed.add_field(name="Genres",
                        value=get_genres(data['genres']),
                        inline=True)
        embed.add_field(name="Platforms",
                        value=get_platforms(data['platforms']),
                        inline=True)
        embed.add_field(name="Release Date",
                        value=get_release_date(data['release_date']),
                        inline=True)
        embed.set_image(url=data['header_image'])
        return embed
    else:
        return None
