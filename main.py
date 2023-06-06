#!/usr/bin/env python3

import asyncio
import websockets

async def stringing(websocket, string_tab):
    if string_tab[1] == "challstr":
        await websocket.send("|/autojoin lobby")
        print("> |/join lobby")

async def hello():
    async with websockets.connect('ws://sim.smogon.com:8000/showdown/websocket') as websocket:
        while True:
            message = await websocket.recv()
            print("< {}".format(message))
            await stringing(websocket, message.split('|'))

asyncio.get_event_loop().run_until_complete(hello())