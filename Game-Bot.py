import discord
import asyncio
import urllib.request

client = discord.Client() # Creating bot instance

@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('------') # To show that the bot can log in

@client.event
async def on_message(message):
    if message.content.startswith('!game help'):

        await client.send_message(message.channel, 'Simply type !game followed by the game you wished to be linked to on Steam!')

    elif message.content.startswith('!game'): #When !game is entered in chat
        gameName = message.content[6:]
        noSpaceName = gameName.replace(" ", "+")
        if gameName == "csgo": # To bypass API shortcomings for popular games

        	await client.send_message(message.channel, "http://store.steampowered.com/app/730") 

        elif gameName == "pubg":

        	await client.send_message(message.channel, "http://store.steampowered.com/app/578080")

        elif len(gameName) > 0:

        	await client.send_message(message.channel, "Looking for " + gameName.title() + "...")

        	urllink = "http://store.steampowered.com/search/suggest?term=" + noSpaceName + "&f=games"
        	#print(urllink)
        	data = urllib.request.urlopen(urllink)
        	html = data.read()
        	data.close()
        	gameIDLocation = str(html[50:60])
        	gameID = ''.join(filter(lambda x: x.isdigit(), list(gameIDLocation)))
        	if len(gameID) == 0:
        		await client.send_message(message.channel, "Try again with more characters or a different game!")
        	else:
        		await client.send_message(message.channel, "http://store.steampowered.com/app/" + gameID)

        else:

        	await client.send_message(message.channel, "Please enter your search term!")



client.run('TOKEN')
client.change_status("Type !game help for instructions!")