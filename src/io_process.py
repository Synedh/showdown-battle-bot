#!/usr/bin/env python3
import time
from enum import Enum
from xmlrpc.client import Boolean

from src import senders
from src.battlelog_parsing import battlelog_parsing
from src.login import log_in, USERNAME, OWNER
from src.battle import Battle

battles = []
nb_fights_max = 1
nb_fights_simu_max = 1
nb_fights = 0

formats = [
    "gen8randombattle",
    "gen8monotyperandombattle",
    "gen8hackmonscup",
    "gen8challengecup1v1",
    "gen6battlefactory",
    "gen8bssfactory"
]

class Usage(Enum):
    STANDBY = 0
    CHALL_OWNER = 1
    SEARCH = 2


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


def log_battle_result(win: bool):
    with open("log.txt", "r+") as file:
        nb_win, nb_loose, total = file.read().split('/')
        file.seek(0)
        if win:
            file.write(f'{int(nb_win) + 1}/{nb_loose}/{int(total) + 1}')
        else:
            file.write(f'{nb_win}/{int(nb_loose) + 1}/{int(total) + 1}')



async def battle_tag(message, usage):
    """
    Main in fuction. Filter every message sent by server and launch corresponding function.
    :param websocket: Websocket stream.
    :param message: Message received from server. Format : room|message1|message2.
    :param usage: 0: Only recieving. 1 Challenging Synedh. 2 searching random battles.
    """
    global battles
    lines = message.splitlines()
    battle = check_battle(battles, lines[0].split("|")[0].split(">")[1])
    sender = senders.Sender()
    for line in lines[1:]:
        current = line.split('|')
        if len(current) < 2:
            continue
        _, command, *other = current
        try:
            match command:
                case 'init':
                    # Creation de la bataille
                    battle = Battle(lines[0].split("|")[0].split(">")[1])
                    battles.append(battle)
                    await sender.send(battle.battletag, "Hi")
                    await sender.send(battle.battletag, "/timer on")
                case 'player' if other[1] == USERNAME:
                    # Récupérer l'id joueur du bot
                    battle.player_id = other[0]
                    battle.turn += int(other[0].split('p')[1]) - 1
                case "request" if other[0] != '':
                    # Maj team bot
                    if len(other[0]) == 1:
                        await battle.req_loader(other[1].split('\n')[1])
                    else:
                        await battle.req_loader(other[0])
                case "teampreview":
                    # Selection d'ordre des pokemons
                    await battle.make_team_order()
                case "turn":
                    # Phase de reflexion
                    await battle.make_action()
                case "callback" if other[0] == "trapped":
                    await battle.make_move()
                case "win":
                    await sender.send(battle.battletag, "wp")
                    await sender.leaving(battle.battletag)
                    battles.remove(battle)
                    if usage == Usage.SEARCH:
                        log_battle_result(USERNAME in other[0])
                case _:
                    # Send to battlelog parser.
                    battlelog_parsing(battle, command, other)
        except Exception as e:
            await sender.send(battle.battletag, 'Sorry, I crashed.')
            await sender.forfeit(battle.battletag)
            time.sleep(1)
            raise e


async def private_message(user, _, content, *other):
    """
    Handle private message commands.
    :param sender: Sender of the private message.
    :param content: Message sent by user.
    :param other: Other informations sent with pipes.
    """
    sender = senders.Sender()

    if content.startswith('.'):
        if content == '.help':
            await sender.send('', f'/pm {user}, Showdown Battle Bot. Active for {", ".join(formats[:-1])} and {formats[-1]}.')
            await sender.send('', f'/pm {user}, Please challenge me to test your skills.')
        else:
            await sender.send('', f'/pm {user}, Unknown command, type ".help" for help.')
    elif content.startswith('/challenge'):
        # If somebody challenges the bot
        if not len(other):
            # Bot challenge rejected.
            pass
        elif other[0] in formats:
            await sender.send('', f'/accept {user}')
        else:
            await sender.send('', '/challenge')
            await sender.send('', f'/pm {user}, Sorry, I accept only solo randomized metas.')



async def stringing(message, usage=Usage.STANDBY):
    """
    First filtering function on received messages.
    Handle challenge and research actions.
    :param message: Message received from server. Format : room|message1|message2.
    :param usage: 0: Only recieving. 1 Challenging Synedh. 2 searching random battles.
    """
    sender = senders.Sender()
    room, command, *content = message.split('|')

    match command:
        case 'challstr':
            # If we got the challstr, we now can log in.
            await log_in(content[0], content[1])
        case 'updateuser' if USERNAME in content[0] and usage == Usage.CHALL_OWNER:
            # Logged in and chall owner.
            await sender.challenge(OWNER, formats[0])
        case 'updateuser' if USERNAME in content[0] and usage == Usage.SEARCH:
            # Logged in and search battle.
            await sender.searching(formats[0])
            nb_fights += 1
        case 'deinit' if Usage.SEARCH and nb_fights < nb_fights_max:
            # If previous fight is over, we're in search usage and it remains fights
            await sender.searching(formats[0])
            nb_fights += 1
        case 'deinit' if Usage.SEARCH and nb_fights >= nb_fights_max and len(battles) == 0:
            # If previous fight is over, we're in search usage and it don't remains fights
            exit(0)
        case 'pm' if USERNAME not in content[0]:
            await private_message(*content)
        case _ if '|inactive|Battle timer is ON:' in message and usage == Usage.SEARCH:
            # If previous fight has started and we can do more simultaneous fights and we're in search usage.
            if len(battles) < nb_fights_simu_max and nb_fights < nb_fights_max:
                await sender.searching(formats[0])
                nb_fights += 1
    if "battle" in room:
        # Battle concern message.
        await battle_tag(message, usage)
