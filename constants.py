import re
from sqlitedict import SqliteDict

SEARCH_SUGGEST_URL = "https://store.steampowered.com/search/suggest"
STORE_BASE_URL = "https://store.steampowered.com/app/"
APPID_REGEX = re.compile("steam/apps/([0-9]+)/")
CRY_EMOJI = "\U0001F622"
SOB_EMOJI = "\U0001F62D"
EMBED_COLOR = 0xffffff
INVALID_GAME_NAME = ("Please try again with fewer characters, "
                     "the game's full name, or with a different game.")
BOT_AUTHOR = "<@156971607057760256>"
SOURCE_INFO = ("Game-Bot is written in Python, using Discord.py as an API "
               "wrapper for Discord. "
               "The bot was coded by %s, a student at the "
               "University of Waterloo in Canada." % BOT_AUTHOR)
BOT_IMAGE = ("https://images.discordapp.net/avatars/397546577314578433/"
              "de563a0727274f7d5547d13e3f4fd7c1.png?size=64")


HELP_URL = "https://discord.gg/AZTP5fK"
HELP_COUNTRY_VAL = "Set the country from which to display game prices."
HELP_STATS_VAL = "Get statistics about the server Game-Bot is running on."
HELP_BUGS_VAL = ("Get a link to Game-Bot's guild, where you can "
                 "report any bugs or issues you find.")
HELP_SOURCE_VAL = ("Get the Github repository for Game-Bot. You are welcome "
                   "to make a pull request!")
HELP_FOOTER = ("Psst. Add a backslash to find a game that starts with "
               "\"help\", \"bugs\", \"stats\", or \"source\" :]")


user_preferences_dict = SqliteDict('./user_preferences.db', autocommit=True)

game_exceptions = {
    "cs:go": "https://store.steampowered.com/app/730",
    "n++": "https://store.steampowered.com/app/230270",
    "gta 5": "https://store.steampowered.com/app/271590",
    "fortnite": "https://www.epicgames.com/fortnite",
    "overwatch": "https://playoverwatch.com",
    "hearthstone": "https://playhearthstone.com",
    "league of legends": "https://leagueoflegends.com",
    "lol": "https://leagueoflegends.com",
    "osu": "https://osu.ppy.sh",
    "osu!": "https://osu.ppy.sh",
    "roblox": "https://roblox.com",
    "forza horizon 4": "https://www.microsoft.com/en-us/p/forza-horizon-4/9pnqkhfld2wq",
    "gta 4": "https://store.steampowered.com/app/901583",
    "gta iv": "https://store.steampowered.com/app/901583",
    "minecraft": "https://minecraft.net"
}
