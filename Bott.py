"""
UNEXPECTED
This is a python program to create a tournament bot for Dofus.

Version : 0.1
1st version deployed on Vultr serv.

Authors :
*Popoelo
"""

# IMPORTS

import discord
import gspread_formatting
from discord.ext.commands import Bot
import gspread
from gspread_formatting import *
import datetime as datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import var
import token_creds
import date_f


#ASYNC SCHEDULER
sched = AsyncIOScheduler()


#BOT
intents = discord.Intents.all()
bot = Bot(command_prefix="$", intents=intents)  # The command prefix is a required argument, but will never be used


#PRIVATE VAR
cpt = 1
not_cpt = 0


#GSHEET
gc = gspread.service_account(filename=token_creds.json_google_api)
sh = gc.open_by_key(token_creds.ICHI_NI_SAN_google_key)
wks1 = sh.get_worksheet(0)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.event
async def on_message(message):
    if message.content.startswith("$"):
        if message.author.id != var.bot_id:
            infos = await get_infos(message)
            await parser_infos(infos)
            if infos[4] == 'DM':
                sender = bot.get_guild(var.guild_id).get_member(infos[0])
            else:
                sender = message.author
            for c in sender.roles:
                if c.id == var.role_id_orga:
                    if message.content == "$stop bot":
                        var.emergency = True
                    elif message.content == "$run bot":
                        var.emergency = False
                    if not var.emergency:
                        if message.content.startswith("$match"):
                            await schedule_match(message)
                if c.id == var.role_id_arbitre or c.id == var.role_id_orga:
                    if not var.emergency:
                        if message.content.startswith("$setarbitre"):
                            await set_arbitre(message)
                        if message.content.startswith("$setwinner"):
                            await set_winner(message)
            if not var.emergency:
                if message.content.startswith("$compo"):
                    await composition(message, infos)
                if message.content.startswith("$arbitre"):
                    await get_arbitre(message)


async def composition(_message, _infos):
    '''Permet d'inscrire sa composition sur le gsheet via une commande au bot'''
    compo = [0] * var.TEAM_SIZE
    match_IDs = wks1.col_values(var.ID_column)
    if _infos[4] == 'DM':
        if _infos[3] == cpt:
            for id in match_IDs:
                if _message.content.split()[1] == id:
                    if wks1.cell(match_IDs.index(id) + 1, var.Annonce_column).value == '1':
                        await _message.author.dm_channel.send(":flag_fr: Match dans moins d'1h, commande refusée.\n"
                                                              ":flag_gb: Match in less than 1h, command not allowed.")
                        return
                    if len(_message.content.split()[var.offset:]) == 6:
                        for i in range(0, var.TEAM_SIZE):
                            compo[i] = _message.content.split()[i+var.offset]
                        if bot.get_guild(var.guild_id).get_role(_infos[2]).name == \
                                wks1.cell(match_IDs.index(id) + 1, var.A_column).value:
                            wks1.update_cell(match_IDs.index(id) + 1, var.OsA_column, compo[0])
                            wks1.update_cell(match_IDs.index(id) + 1, var.TsA_column, f"{compo[1]} / {compo[2]}")
                            wks1.update_cell(match_IDs.index(id) + 1, var.THsA_column, f"{compo[3]} / {compo[4]} / {compo[5]}")
                            await _message.add_reaction(await bot.get_guild(var.guild_id).fetch_emoji(var.CheckMark_id))
                        elif bot.get_guild(var.guild_id).get_role(_infos[2]).name == \
                                wks1.cell(match_IDs.index(id) + 1, var.B_column).value:
                            wks1.update_cell(match_IDs.index(id) + 1, var.OsB_column, compo[0])
                            wks1.update_cell(match_IDs.index(id) + 1, var.TsB_column, f"{compo[1]} / {compo[2]}")
                            wks1.update_cell(match_IDs.index(id) + 1, var.THsB_column, f"{compo[3]} / {compo[4]} / {compo[5]}")
                            await _message.add_reaction(await bot.get_guild(var.guild_id).fetch_emoji(var.CheckMark_id))
                    else:
                        await _message.author.dm_channel.send(":flag_fr: Composition non complète ou ID incorrect\n"
                                                              ":flag_gb: Team size not respected or incorrect ID.")
                        return
        else:
            await _message.author.dm_channel.send(":flag_fr: Vous n'êtes pas capitaine de votre équipe\n"
                                                  ":flag_gb: You're not the captain.")
            return
    else:
        await _message.channel.send(":flag_fr: Merci d'envoyer votre composition en MP au bot\n"
                                    ":flag_gb: Please send your team comp to the bot via private message.")
        return


async def set_arbitre(_message):
    '''Permet de set l'arbitre du match sur le gsheet'''
    match_IDs = wks1.col_values(var.ID_column)
    arbitres = ""
    for id in match_IDs:
        if id == _message.content.split()[1]:
            tempArbitre = wks1.cell(int(id)+var.offset, var.Arbitre_column).value
            for k in range(0, len(_message.content.split())-2):
                arbitres += _message.content.split()[2+k] + " "
                wks1.update_cell(match_IDs.index(id) + 1, var.Arbitre_column, arbitres)
                await _message.add_reaction(await bot.get_guild(var.guild_id).fetch_emoji(var.CheckMark_id))
            if tempArbitre != '':
                await _message.channel.send(f"Le(s) ancien(s) arbitre(s) {tempArbitre} ont été remplacés par"
                                            f" {wks1.cell(int(id)+var.offset, var.Arbitre_column).value}")


async def set_winner(_message):
    match_IDs = wks1.col_values(var.ID_column)
    for id in match_IDs:
        if id == _message.content.split()[1]:
            if _message.content.split()[2].startswith("<@&"):
                winner = bot.get_guild(var.guild_id).get_role(int(_message.content.split()[2][3:-1])).name
                wks1.update_cell(match_IDs.index(id) + 1, var.Vainqueur_column, winner)
                fmt = gspread_formatting.CellFormat(backgroundColor=Color(0.84, 1, 0.59))
                row = 'B' + str(int(id) + var.offset) + ':' + 'O' + str(int(id)+var.offset)
                format_cell_range(wks1, row, fmt)
                await _message.add_reaction(await _message.guild.fetch_emoji(var.CheckMark_id))


async def get_infos(_message):
    '''Permet d'obtenir des informations relatives au message envoyé'''
    infos = [0]*10
    infos[0] = _message.author.id
    infos[1] = _message.content
    if bot.get_guild(var.guild_id) is not None:
        for c in bot.get_guild(var.guild_id).get_member(infos[0]).roles:
            if c.id == var.role_id_cpt:
                infos[3] = cpt
                break
            if c.id in var.teams_id:
                infos[2] = bot.get_guild(var.guild_id).get_role(c.id).id
    if _message.channel.type is discord.ChannelType.private:
        infos[4] = 'DM'
    else:
        infos[4] = _message.channel.id
    if _message.guild is not None:
        infos[5] = _message.guild.id
    else:
        infos[5] = "None"
    return infos


async def parser_infos(_infos):
    '''Permet de parser le buffer infos'''
    msg = f"Auteur du message : {str(bot.get_user(_infos[0]).mention)}\n"
    msg += f"Le message contenait : {_infos[1]}\n"
    if _infos[4] == 'DM':
        msg += f"Le message a été envoyé en privé" + "\n"
    else:
        msg += f"Le message a été posté dans le channel " \
               f"{str(bot.get_guild(_infos[5]).get_channel(_infos[4]).mention)} du serveur " \
               f"{str(bot.get_guild(_infos[5]))}\n"
    await bot.get_guild(var.guild_id).get_channel(var.poubelle_id).send(msg)


async def date_observer():
    '''Routine qui vient scruter quand un match va arriver et l'annonce si c'est le cas'''
    if not var.emergency:
        dateList = wks1.col_values(var.time_column)
        announced = wks1.col_values(var.Annonce_column)
        if len(dateList) <= 1:
            return
        if len(announced) <= 1:
            return
        for date in dateList[2:]:
            if date != '':
                n_date = await date_f.split_date(date)
                calendar = n_date[0][2] + n_date[0][1] + n_date[0][0]
                timed = n_date[1][0] + n_date[1][1]

                mDate = datetime.datetime(year=int(calendar[0:4]), month=int(calendar[4:6]), day=int(calendar[6:]), hour=int(timed[0:2]), minute=int(timed[2:]))
                nDate = datetime.datetime.now()
                tdelta = mDate - nDate
                if tdelta.days == 0 and mDate.date() - nDate.date() != 0:
                    print(tdelta.total_seconds())
                    if tdelta.total_seconds() <= var.deadline:
                        if announced[dateList.index(date)] == '0':
                            wks1.update_cell(dateList.index(date) + 1, var.time_column + 1, '1')
                            await alert_match_local(dateList.index(date) + 1)


async def alert_match_public(_num):
    '''Fonction qui alerte lorsqu'un match va se dérouler, dans le channel fights to come'''
    team_list = await bot.get_guild(var.guild_id).fetch_roles()
    for team in team_list:
        if team.name == wks1.cell(_num, var.A_column).value:
            teamA = team.mention
        elif team.name == wks1.cell(_num, var.B_column).value:
            teamB = team.mention
    msg = f"{bot.get_guild(var.guild_id).get_role(var.match_role_id).mention}\n"
    msg += f":crossed_swords: {teamA} vs {teamB} :crossed_swords:\n"
    msg += f":alarm_clock: {wks1.cell(_num, var.time_column).value.split()[0]}" \
           f" - {wks1.cell(_num, var.time_column).value.split()[1]} (FR)\n" \
           f"MAP : {wks1.cell(_num,var.Map_column).value}\n"
    await bot.get_guild(var.guild_id).get_channel(var.fights_to_come_id).send(msg)


async def alert_match_local(_num):
    '''Fonction qui alerte lorsqu'un match va se dérouler, dans le channel associé'''
    chann_list = await bot.get_guild(var.guild_id).fetch_channels()
    local_chann = None
    for chann in chann_list:
        if chann.name.split("-")[0] == str(_num-var.offset):
            local_chann = chann.id
    if local_chann is not None:
        msg = f"@here\n" \
              f":flag_fr: Vos équipes s'affronteront dans 1 heure. Voici les compositions que vous avez choisi :\n" \
              f":flag_gb: The match is scheduled in 1h. There are the team comps both of your teams chose to play with:\n\n"
        msg += f"{wks1.cell(_num,var.A_column).value} :crossed_swords: {wks1.cell(_num,var.B_column).value}\n \n"
        msg += f"Pour le 1V1 / For the 1V1 :\n"
        msg += f"{wks1.cell(_num,var.OsA_column).value} :vs: {wks1.cell(_num,var.OsB_column).value}\n \n"
        msg += f"Pour le 2V2 / For the 2V2 :\n"
        msg += f"{wks1.cell(_num,var.TsA_column).value} :vs: {wks1.cell(_num,var.TsB_column).value}\n \n"
        msg += f"Pour le 3V3 / For the 3V3 :\n"
        msg += f"{wks1.cell(_num,var.THsA_column).value} :vs: {wks1.cell(_num,var.THsB_column).value}"

        message = await bot.get_guild(var.guild_id).get_channel(local_chann).send(msg)
        await message.pin()


async def schedule_match(_message):
    '''Fonction qui permet à un organisateur d'écrire dans le gsheet quant aux informations d'un match'''
    if len(_message.content.split()) != 7:
        await _message.channel.send("Format incorrect.\n $match ID equipeA equipeB jj/mm/aaaa hh/mm map")
        return
    match_IDs = wks1.col_values(var.ID_column)
    for id in match_IDs:
        if id == _message.content.split()[1]:
            if wks1.cell(match_IDs.index(id) + 1, var.Annonce_column).value == '0':
                #EQUIPE A and B
                if _message.content.split()[2].startswith("<@&") and _message.content.split()[3].startswith("<@&"):
                    teamA = bot.get_guild(var.guild_id).get_role(int(_message.content.split()[2][3:-1])).name
                    wks1.update_cell(match_IDs.index(id) + 1, var.A_column, teamA)
                    teamB = bot.get_guild(var.guild_id).get_role(int(_message.content.split()[3][3:-1])).name
                    wks1.update_cell(match_IDs.index(id) + 1, var.B_column, teamB)
                else:
                    await _message.channel.send("Merci de bien tag les team")
                    return
                #DATE ET HEURE
                time = str(_message.content.split()[4]) + " " + str(_message.content.split()[5])
                wks1.update_cell(match_IDs.index(id) + 1, var.time_column, time)
                #MAP
                wks1.update_cell(match_IDs.index(id) + 1, var.Map_column, _message.content.split()[6])
                await _message.add_reaction(await _message.guild.fetch_emoji(var.CheckMark_id))
                await alert_match_public(match_IDs.index(id) + 1)
            else:
                await _message.channel.send("Désolé, le match a déjà été annoncé.")


async def get_arbitre(_message):
    '''Permet de voir l'arbitre du match'''
    match_IDs = wks1.col_values(var.ID_column)
    for id in match_IDs:
        if id == _message.content.split()[1]:
            arbitres = wks1.cell(int(id) + var.offset, var.Arbitre_column).value
            await _message.channel.send(f":flag_fr: Le(s) arbitre(s) de la rencontre est(sont) : {arbitres}\n"
                                        f":flag_gb: The referee(s) of the match is(are) : {arbitres}")
            await _message.author.dm_channel.send(f":flag_fr: Le(s) arbitre(s) de la rencontre est(sont) : {arbitres}\n"
                                                  f":flag_gb: The referee(s) of the match is(are) : {arbitres}")


#ASYNC THREAD
sched.add_job(date_observer, 'interval', seconds=30)
sched.start()


# Run the bot with the token
bot.run(token_creds.token)

