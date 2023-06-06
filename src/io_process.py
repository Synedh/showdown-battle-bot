#!/usr/bin/env python3

from src.login import log_in
from src.battle import Battle
from src import senders

battles = []
nb_fights = 2
nb_fights_done = 0


def check_battle(battle_list, room_id):
    """
    Get Battle corresponding to room_id.
    :param battle_list: Array of Battle.
    :param room_id: Id of Battle.
    :return: Battle.
    """
    for battle in battle_list:
        if battle.room_id == room_id:
            return battle
    return None

async def battle_tag(websocket, message):
    """
    Main in fuction. Filter every message sent by server and launch corresponding function.
    :param websocket: Websocket stream.
    :param message: Message received from server. Format : room|message1|message2.
    """
    global battles
    lines = message.splitlines()
    battle = check_battle(battles, lines[0].split('-')[len(lines[0].split('-')) - 1])
    for line in lines[1:]:
        try:
            current = line.split('|')
            if current[1] == "init":
                # Creation de la bataille
                battles.append(Battle(lines[0].split('-')[len(lines[0].split('-')) - 1]))
                await senders.sendmessage(websocket, battles[len(battles) - 1].room_id, "Hi")
                await senders.sendmessage(websocket, battles[len(battles) - 1].room_id, "/timer on")
            elif current[1] == "player" and len(current) > 3 and current[3].lower() == "suchtestbot":
                # Récupérer l'id joueur du bot
                battle.set_player_id(current[2])
            elif current[1] == "request":
                # Maj team bot
                await battle.req_loader(current[2], websocket)
            elif current[1] == "switch" and battle.player_id not in current[2]:
                # Récupérer le nom du pkm pour l'ajouter/maj à la team ennemie
                battle.update_enemy(current[3].split(',')[0], current[4])
            elif current[1] == "turn":
                # Phase de reflexion
                await battle.make_action(websocket)
            elif current[1] == "-status":
                battle.update_status_enemy(current[3])
            elif current[1] == "-item" and battle.player_id not in current[2]:
                battle.set_enemy_item(current[3])
            elif current[1] == "-enditem" and battle.player_id not in current[2]:
                battle.set_enemy_item("")
            elif current[1] == "callback" and current[2] == "trapped":
                await battle.make_move(websocket)
            elif current[1] == "win":
                await senders.sendmessage(websocket, battle.room_id, "wp")
                await senders.leaving(websocket, battle.room_id)
            elif current[1] == "c":
                # This is a message
                pass
        except IndexError:
            pass

async def stringing(websocket, message):
    """
    First filtering function on received messages.
    Handle challenge and research actions.
    :param websocket: Websocket stream.
    :param message: Message received from server. Format : room|message1|message2.
    """
    global nb_fights
    global nb_fights_done
    string_tab = message.split('|')
    if string_tab[1] == "challstr":
        # Si la challstr a  été encoyee, on peut se connecter
        await log_in(websocket, string_tab[2], string_tab[3])
    elif string_tab[1] == "updateuser" and string_tab[2] == "SuchTestBot":
        # Si on est log, alors on peut commencer les combats
        pass
        # await senders.searching(websocket)
        # await senders.challenge(websocket, "Synedh")
    elif "updatechallenges" in string_tab[1]:
        # Si quelqu'un envoie un challenge, alors accepter
        try:
            if string_tab[2].split('\"')[3] != "challengeTo":
                if string_tab[2].split('\"')[5] == "gen7randombattle":
                    await senders.sender(websocket, "", "/accept " + string_tab[2].split('\"')[3])
                else:
                    await senders.sender(websocket, "", "/reject " + string_tab[2].split('\"')[3])
                    await senders.sender(websocket, "", "/pm " + string_tab[2].split('\"')[3]
                                         + ", Sorry, I accept only [Gen 7] Random Battle challenges.")
        except KeyError:
            pass
    elif "battle" in string_tab[0]:
        # Si on recoit un message dans une interface de combat
        await battle_tag(websocket, message)
