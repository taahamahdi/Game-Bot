# Game-Bot

This Discord bot takes in a Steam game's name and returns its link on the Steam Store based on Valve's search suggest feature.

[![Discord Bots](https://discordbots.org/api/widget/397546577314578433.svg)](https://discordbots.org/bot/397546577314578433)

## Dependencies

`discord.py`, `lxml`, `aiohttp`, `sqlitedict`, `psutil`, `dblpy`:
```
python3 -m pip install --user discord.py lxml aiohttp sqlitedict psutil dblpy
```

Set the environment variable `GAME_BOT_TOKEN` as your token, eg.

```
export GAME_BOT_TOKEN=foobar
python3 game_bot.py
```

If you have `HISTCONTROL` set to `ignoreboth` or `ignorespace` in bash,
prepend a space before any command containing your token to prevent it from
showing up in your history.

**Make sure you are running Python 3.4.2+!**
