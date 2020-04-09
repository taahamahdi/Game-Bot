import dbl
import discord
from discord.ext import commands, tasks

import aiohttp
import asyncio
import logging

class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = 'dbl_token'  # set this to your DBL token
        self.dblpy = dbl.DBLClient(self.bot, self.token)

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your
        server count"""
        logger.info('attempting to post server count')

        try:
            await self.dblpy.post_guild_count()
            logger.info('posted server count ({})'
                        .format(self.dblpy.guild_count()))
        except Exception as e:
            logger.exception('Failed to post server count\n{}: {}'
                             .format(type(e).__name__, e))
        await asyncio.sleep(1800)


def setup(bot):
    global logger
    logger = logging.getLogger('bot')
    bot.add_cog(TopGG(bot))
