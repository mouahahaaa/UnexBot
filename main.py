import discord
import numpy as np

default_intents = discord.Intents.default()
default_intents.members = True

client = discord.Client(intents=default_intents)

fiveMatrixPoints = np.zeros((5,2))
fiveTeamSize = 5
fiveBufferCommandPlayers = 3

@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_message(message):
    if message.content.startswith("!u"):

        if message.content.split()[1] == "-w":
            await message.channel.send("C'est une win")
        elif message.content.split()[1] == "-l":
            await message.channel.send("C'est une lose")

#######################################################################################

        if message.content.split()[2] == "-a":
            await message.channel.send("En attaque")
        elif message.content.split()[2] == "-d":
            await message.channel.send("En défense")

#######################################################################################

        for i in range(4):
            fiveMatrixPoints[i,1] = message.content.split()[fiveBufferCommandPlayers + i]



@client.event
async def on_member_join(member):
    client.get_channel()

client.run("OTExNzUyOTE5ODk5MDU0MTAw.YZl-Ew.7w_lJrYjmewUqt0jWJ-TBKKOiYQ")