#!/usr/bin/env python3

import asyncio
import websockets

from login import log_in
from state import Battle
import senders

battle = None

async def battle_tag(websocket, message):
    global battle
    lines = message.splitlines()
    for line in lines[1:]:
        if len(line) > 1:
            current = line.split('|')
            if current[1] == "init":
                battle = Battle(line[0].split('-')[len(line[0].split('-')) - 1])
            elif current[1] == "player" and current[3].lower() == "suchtestnot":
                battle.set_player_id(current[2])
            elif current[1] == "request":
                battle.req_loader(current[2])
            elif current[1] == "switch" and battle.player_id not in current[2]:
                battle.update_enemy(current[3].split(',')[0], current[4])
            elif current[1] == "turn":
                battle.makeMove(current[2])

async def stringing(websocket, message):
    string_tab = message.split('|')
    if string_tab[1] == "challstr":
        # Si la challstr a  été encoyee, on peut se connecter
        await log_in(websocket, string_tab[2], string_tab[3])
    elif string_tab[1] == "updateuser" and string_tab[2] == "SuchTestBot":
        # Si on est log, alors on peut commencer les combats
        await senders.challenge(websocket, "Synedh")
        pass
    # elif "updatechallenges" in string_tab[1]:
    #     await senders.sender(websocket, "", "/accept Synedh", "")
    elif "battle" in string_tab[0]:
        await battle_tag(websocket, message)
        # Si on recoit un message dans une interface de combat

async def main():
    async with websockets.connect('ws://sim.smogon.com:8000/showdown/websocket') as websocket:
        while True:
            message = await websocket.recv()
            print("<< {}".format(message))
            await stringing(websocket, message)

asyncio.get_event_loop().run_until_complete(main())
