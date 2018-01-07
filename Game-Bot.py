import discord
import asyncio
import urllib.request

# Game-Bot.py contains some functions based on Rapptz's Discord.py's bot examples
#
#                    https://github.com/Rapptz/discord.py

client = discord.Client() # Creating bot instance

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
        gameName = message.content[6:]
        noSpaceName = gameName.replace(" ", "+")
        if gameName.lower() == "csgo" or gameName.lower() == "cs" or gameName.lower() == "cs:go": 
            # To bypass API shortcomings for popular games

            await client.send_message(message.channel, "http://store.steampowered.com/app/730") 

        elif gameName.lower() == "pubg":
            
            await client.send_message(message.channel, "http://store.steampowered.com/app/578080")

        elif gameName.lower() == "n++":

            await client.send_message(message.channel, "http://store.steampowered.com/app/230270")

        elif gameName.lower() == "gta" or gameName.lower() == "gta5" or gameName.lower() == "gtav" \
          or gameName.lower() == "gta 5" or gameName.lower() == "gta v":

            await client.send_message(message.channel, "http://store.steampowered.com/app/271590")

        elif len(gameName) > 0:

            urllink = "http://store.steampowered.com/search/suggest?term=" + noSpaceName + "&f=games"

            try:
                data = urllib.request.urlopen(urllink)
                html = data.read()
                data.close()
                gameIDLocation = str(html[50:60])
                gameID = ''.join(filter(lambda x: x.isdigit(), list(gameIDLocation)))
                # print(len(gameID))

                if len(gameID) == 0:

                    await client.send_message(message.channel, "Try again with more characters or a different game!")

                else:

                    await client.send_message(message.channel, "http://store.steampowered.com/app/" + gameID)

            except ValueError:
                await client.send_message(message.channel, "Game not found :(")

        else:

        	await client.send_message(message.channel, "Please enter your search term!")


client.run('TOKEN')
