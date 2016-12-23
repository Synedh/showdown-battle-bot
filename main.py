#!/usr/bin/env python3

import asyncio
import websockets

from login import log_in
from state import Battle
import senders

battles = []


def check_battle(battle_list, room_id):
    for battle in battle_list:
        if battle.room_id == room_id:
            return battle
    return None


async def battle_tag(websocket, message):
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
            elif current[1] == "player" and len(current) > 3 and current[3].lower() == "suchtestbot":
                # Récupérer l'id joueur du bot
                battle.set_player_id(current[2])
            elif current[1] == "request":
                # Maj team bot
                battle.req_loader(current[2])
            elif current[1] == "switch" and battle.player_id not in current[2]:
                # Récupérer le nom du pkm pour l'ajouter/maj à la team ennemie
                    battle.update_enemy(current[3].split(',')[0], current[4])
            elif current[1] == "turn":
                # Phase de reflexion
                await battle.make_move(websocket, current[2])
            elif current[1] == "win":
                await senders.leaving(websocket, battle.room_id)
            elif current[1] == "c":
                # This is a message
                pass
        except IndexError:
            pass

async def stringing(websocket, message):
    string_tab = message.split('|')
    if string_tab[1] == "challstr":
        # Si la challstr a  été encoyee, on peut se connecter
        await log_in(websocket, string_tab[2], string_tab[3])
    elif string_tab[1] == "updateuser" and string_tab[2] == "SuchTestBot":
        # Si on est log, alors on peut commencer les combats
        await senders.challenge(websocket, "Synedh")
    elif "updatechallenges" in string_tab[1]:
        # Si synedh envoie un challenge, alors accepter
        try:
            if string_tab[2].split('\"')[3] != "challengeTo":
                await senders.sender(websocket, "", "/accept " + string_tab[2].split('\"')[3], "")
        except:
            pass
    elif "battle" in string_tab[0]:
        # Si on recoit un message dans une interface de combat
        await battle_tag(websocket, message)


async def main():
    async with websockets.connect('ws://sim.smogon.com:8000/showdown/websocket') as websocket:
        while True:
            message = await websocket.recv()
            print("<< {}".format(message))
            await stringing(websocket, message)


asyncio.get_event_loop().run_until_complete(main())
