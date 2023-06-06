#!/usr/bin/env python3

import asyncio
import websockets
import requests

async def log_in(websocket, challstr):
    logfile = open("id.txt")
    username = logfile.readline()[:-1]
    password = logfile.readline()[:-1]
    logfile.close()
    datastr = "act=login&name=" + username + "&pass=" + password + "&challstr=" + challstr
    print(challstr[len(challstr) - 1])
    resp = requests.post("http://play.pokemonshowdown.com/action.php",
                  data=datastr)
    print(str(resp.status_code))
    print(str(resp.headers))
    print(str(resp.encoding))
    print(str(resp.text))
    print(str(resp.json()))

async def stringing(websocket, string_tab):
    if string_tab[1] == "challstr":
        # await websocket.send("|/join lobby")
        # print("> |/join lobby")
        await log_in(websocket, string_tab[3])

async def hello():
    async with websockets.connect('ws://sim.smogon.com:8000/showdown/websocket') as websocket:
        while True:
            message = await websocket.recv()
            print("< {}".format(message))
            await stringing(websocket, message.split('|'))

asyncio.get_event_loop().run_until_complete(hello())