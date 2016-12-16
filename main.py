#!/usr/bin/env python3

import asyncio
import websockets

from login import log_in

async def stringing(websocket, string_tab):
    if string_tab[1] == "challstr":
        # Si la challstr a  été encoyée, on peut se connecter
        await log_in(websocket, string_tab[2], string_tab[3])
    elif string_tab[1] == "updateuser" and string_tab[2] == "SuchTestBot":
        # Si on est loggé, alors on peut commencer les combats
        pass
    elif "battle" in string_tab[0]:
        # Si on reçoit un message dans une interfacede combat
        print("Battlelog")

async def main():
    async with websockets.connect('ws://sim.smogon.com:8000/showdown/websocket') as websocket:
        while True:
            message = await websocket.recv()
            print("<< {}".format(message))
            await stringing(websocket, message.split('|'))

asyncio.get_event_loop().run_until_complete(main())
