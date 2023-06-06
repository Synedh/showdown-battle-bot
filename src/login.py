import sys
import json
import requests

from src.senders import sender

async def log_in(websocket, challid, chall):
    """
    Login in function. Send post request to showdown server.
    :param websocket: Websocket stream
    :param challid: first part of login challstr sent by server
    :param chall: second part of login challstr sent by server
    """
    with open(sys.path[0] + "/src/id.txt") as logfile:
        username = logfile.readline()[:-1]
        password = logfile.readline()[:-1]
    resp = requests.post("https://play.pokemonshowdown.com/action.php?",
                         data={
                            'act': 'login',
                            'name': username,
                            'pass': password,
                            'challstr': challid + "%7C" + chall
                         })
    await sender(websocket, "", "/trn " + username + ",0," + json.loads(resp.text[1:])['assertion'])
    await sender(websocket, "", "/avatar 159")
