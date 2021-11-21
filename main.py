import discord
import numpy as np

default_intents = discord.Intents.default()
default_intents.members = True

client = discord.Client(intents=default_intents)

fiveListPlayers = np.zeros((5, 1), dtype=object)
fiveTeamSize = 5
fiveBufferCommandPlayers = 3
fiveWin = True
fiveAtk = True
fiveBaremeWinAtk = 3 #points gdoc
fiveBaremeLoseAtk = 1 #points gdoc
fiveBaremeWinDef = 2 #points gdoc
fiveBaremeLoseDef = 1 #points gdoc
fivePlayerPoints = 0

@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_message(message):
    if message.content.startswith("!u"):

        if message.content.split()[1] == "-w":
            await message.channel.send("C'est une win")
            fiveWin = True
        elif message.content.split()[1] == "-l":
            await message.channel.send("C'est une lose")
            fiveWin = False

#######################################################################################

        if message.content.split()[2] == "-a":
            await message.channel.send("En attaque")
            fiveAtk = True
        elif message.content.split()[2] == "-d":
            await message.channel.send("En défense")
            fiveAtk = Lose

#######################################################################################

        for i in range(fiveTeamSize):
            fiveListPlayers[i, 0] = message.content.split()[fiveBufferCommandPlayers + i]
            if fiveAtk == True:
                if fiveWin == True:
                    fivePlayerPoints = fiveBaremeWinAtk
                elif fiveWin == False:
                    fivePlayerPoints = fiveBaremeLoseAtk
            elif fiveAtk == False:
                if fiveWin == True:
                    fivePlayerPoints = fiveBaremeWinDef
                elif fiveWin == False:
                    fivePlayerPoints = fiveBaremeLoseDef
        print(fiveListPlayers)


@client.event
async def on_member_join(member):
    client.get_channel()

client.run("OTExNzUyOTE5ODk5MDU0MTAw.YZl-Ew.7w_lJrYjmewUqt0jWJ-TBKKOiYQ")