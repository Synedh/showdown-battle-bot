#!/usr/bin/env python3

from src import senders
from src.battlelog_parsing import battlelog_parsing
from src.login import log_in
from src.battle import Battle

battles = []
nb_fights_max = 20
nb_fights_simu_max = 6
nb_fights = 0

formats = [
    "gen7randombattle",
    "gen7monotyperandombattle",
    "gen7hackmonscup",
    "gen7challengecup1v1",
    "gen6battlefactory",
    "gen7bssfactory"
]


def check_battle(battle_list, battletag) -> Battle or None:
    """
    Get Battle corresponding to room_id.
    :param battle_list: Array of Battles.
    :param battletag: String, Tag of Battle.
    :return: Battle.
    """
    for battle in battle_list:
        if battle.battletag == battletag:
            return battle
    return None

async def battle_tag(websocket, message, usage):
    """
    Main in fuction. Filter every message sent by server and launch corresponding function.
    :param websocket: Websocket stream.
    :param message: Message received from server. Format : room|message1|message2.
    :param usage: 0: Only recieving. 1 Challenging Synedh. 2 searching random battles.
    """
    global battles
    lines = message.splitlines()
    battle = check_battle(battles, lines[0].split("|")[0].split(">")[1])
    for line in lines[1:]:
        try:
            current = line.split('|')
            if current[1] == "init":
                # Creation de la bataille
                battle = Battle(lines[0].split("|")[0].split(">")[1])
                battles.append(battle)
                await senders.sendmessage(websocket, battle.battletag, "Hi")
                await senders.sendmessage(websocket, battle.battletag, "/timer on")
            elif current[1] == "player" and len(current) > 3 and current[3].lower() == "suchtestbot":
                # Récupérer l'id joueur du bot
                battle.player_id = current[2]
                battle.turn += int(current[2].split('p')[1]) - 1
            elif current[1] == "request":
                if current[2] == '':
                    continue;
                # Maj team bot
                if len(current[2]) == 1:
                    try:
                        await battle.req_loader(current[3].split('\n')[1], websocket)
                    except KeyError as e:
                        print(e)
                        print(current[3])
                else:
                    await battle.req_loader(current[2], websocket)
            elif current[1] == "teampreview":
                # Selection d'ordre des pokemons
                await battle.make_team_order(websocket)
            elif current[1] == "turn":
                # Phase de reflexion
                await battle.make_action(websocket)
            elif current[1] == "callback" and current[2] == "trapped":
                await battle.make_move(websocket)
            elif current[1] == "win":
                await senders.sendmessage(websocket, battle.battletag, "wp")
                await senders.leaving(websocket, battle.battletag)
                battles.remove(battle)
                if usage == 2:
                    with open("log.txt", "r+") as file:
                        line = file.read().split('/')
                        file.seek(0)
                        if "suchtestbot" in current[2].lower():
                            file.write(str(int(line[0]) + 1) + "/" + line[1] + "/" + str(int(line[2]) + 1))
                        else:
                            file.write(line[0] + "/" + str(int(line[1]) + 1) + "/" + str(int(line[2]) + 1))
            elif current[1] == "c":
                # This is a message
                pass
            else:
                # Send to battlelog parser.
                battlelog_parsing(battle, current[1:])
        except IndexError:
            pass

async def stringing(websocket, message, usage=0):
    """
    First filtering function on received messages.
    Handle challenge and research actions.
    :param websocket: Websocket stream.
    :param message: Message received from server. Format : room|message1|message2.
    :param usage: 0: Only recieving. 1 Challenging Synedh. 2 searching random battles.
    """
    global nb_fights_max
    global nb_fights
    global nb_fights_simu_max
    global battles
    global formats

    string_tab = message.split('|')
    if string_tab[1] == "challstr":
        # If we got the challstr, we now can log in.
        await log_in(websocket, string_tab[2], string_tab[3])
    elif string_tab[1] == "updateuser" and string_tab[2] == "SuchTestBot":
        # Once we are connected.
        if usage == 1:
            await senders.challenge(websocket, "Synedh", formats[0])
        if usage == 2:
            await senders.searching(websocket, formats[0])
            nb_fights += 1
    elif string_tab[1] == "deinit" and usage == 2:
        # If previous fight is over and we're in 2nd usage
        if nb_fights < nb_fights_max:  # If it remains fights
            await senders.searching(websocket, formats[0])
            nb_fights += 1
        elif nb_fights >= nb_fights_max and len(battles) == 0:  # If it don't remains fights
            exit(0)
    elif "|inactive|Battle timer is ON:" in message and usage == 2:
        # If previous fight has started and we can do more simultaneous fights and we're in 2nd usage.
        if len(battles) < nb_fights_simu_max and nb_fights < nb_fights_max:
            await senders.searching(websocket, formats[0])
            nb_fights += 1
    elif "updatechallenges" in string_tab[1]:
        # If somebody challenges the bot
        try:
            if string_tab[2].split('\"')[3] != "challengeTo":
                if string_tab[2].split('\"')[5] in formats:
                    await senders.sender(websocket, "", "/accept " + string_tab[2].split('\"')[3])
                else:
                    await senders.sender(websocket, "", "/reject " + string_tab[2].split('\"')[3])
                    await senders.sender(websocket, "", "/pm " + string_tab[2].split('\"')[3]
                                         + ", Sorry, I accept only solo randomized metas.")
        except KeyError:
            pass
    elif string_tab[1] == "pm" and "SuchTestBot" not in string_tab[2]:
        if string_tab[4] == ".info":
            await senders.sender(websocket, "", "/pm " + string_tab[2] + ", Showdown Battle Bot. Active for "
                                                                       + ", ".join(formats[:-1]) + " and "
                                                                       + formats[-1] + ".")
            await senders.sender(websocket, "", "/pm " + string_tab[2] + ", Please challenge me to test your skills.")
        else:
            await senders.sender(websocket, "", "/pm " + string_tab[2] + ", Unknown command, type \".info\" for help.")

    if "battle" in string_tab[0]:
        # Battle concern message.
        await battle_tag(websocket, message, usage)
