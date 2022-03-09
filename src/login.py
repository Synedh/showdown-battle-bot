import json
import configparser
from pathlib import Path
import requests

from src.senders import Sender


config = configparser.ConfigParser()
config.read(Path('.').parent.absolute() / 'config.ini')
USERNAME = config['bot']['username']
PASSWORD = config['bot']['password']
OWNER = config['bot']['owner']

async def log_in(challid: str, chall: str):
    """
    Login in function. Send post request to showdown server.
    :param challid: first part of login challstr sent by server
    :param chall: second part of login challstr sent by server
    """
    sender = Sender()
    resp = requests.post('https://play.pokemonshowdown.com/action.php?',
                         data={
                            'act': 'login',
                            'name': USERNAME,
                            'pass': PASSWORD,
                            'challstr': challid + '%7C' + chall
                         })
    await sender.send('', f'/trn {USERNAME},0,{json.loads(resp.text[1:])["assertion"]}')
    await sender.send('', '/avatar lusamine-nihilego')
