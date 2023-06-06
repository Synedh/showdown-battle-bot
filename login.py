import requests
import json

async def log_in(websocket, id, chall):
    logfile = open("id.txt")
    username = logfile.readline()[:-1]
    password = logfile.readline()[:-1]
    logfile.close()
    resp = requests.post("https://play.pokemonshowdown.com/action.php?",
                         data={
                            'act': 'login',
                            'name': username,
                            'pass': password,
                            'challstr': id + "%7C" + chall
                         })
    print(json.loads(resp.text[1:]))
    await websocket.send("|/trn " + username + ",0," + json.loads(resp.text[1:])['assertion'])
    print("> |/trn " + username + ",0," + json.loads(resp.text[1:])['assertion'])
    await websocket.send("|/avatar 159")
    print("> |/avatar 159")