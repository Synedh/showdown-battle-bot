#coding: utf8

import requests
import json

from senders import sender

async def log_in(websocket, id, chall):
    with open("id.txt") as logfile:
        username = logfile.readline()[:-1]
        password = logfile.readline()[:-1]
    resp = requests.post("https://play.pokemonshowdown.com/action.php?",
                         data={
                            'act': 'login',
                            'name': username,
                            'pass': password,
                            'challstr': id + "%7C" + chall
                         })
    # print(json.loads(resp.text[1:]))
    await sender(websocket, "", "/trn " + username + ",0," + json.loads(resp.text[1:])['assertion'], "")
    await sender(websocket, "", "/avatar 159", "")