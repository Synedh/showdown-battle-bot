import json

from ia import make_best_action, make_best_switch
from pokemon import Pokemon, Team, Status

import senders


class Battle:
    def __init__(self, room_id):
        self.bot_team = Team()
        self.enemy_team = Team()
        self.current_pkm = None
        self.turn = 0
        self.room_id = room_id
        self.player_id = ""

    async def req_loader(self, req, websocket):
        jsonobj = json.loads(req)
        self.turn += 1
        objteam = jsonobj['side']['pokemon']
        self.bot_team = Team()
        for pkm in objteam:
            newpkm = Pokemon(pkm['details'].split(',')[0], pkm['condition'], pkm['active'])
            newpkm.load_known([pkm['baseAbility']], pkm['stats'], pkm['moves'])
            self.bot_team.add(newpkm)
        if "forceSwitch" in jsonobj.keys():
            await self.make_switch(websocket)
        elif "active" in jsonobj.keys():
            self.current_pkm = jsonobj["active"]

    def set_player_id(self, player_id):
        self.player_id = player_id

    def update_enemy(self, pkm_name, condition):
        if pkm_name not in self.enemy_team:
            print("** Update enemy - Not yet in team")
            for pkm in self.enemy_team.pokemons:
                pkm.active = False
            pkm = Pokemon(pkm_name, condition, True)
            pkm.load_unknown()
            self.enemy_team.add(pkm)
        else:
            print("** Update enemy - Yet in team")
            # for pkm in self.enemy_team.pokemons:
            #     pkm.active = False

    def update_status_enemy(self, status):
        if status == "tox":
            self.enemy_team.active().status = Status.TOX
        elif status == "brn":
            self.enemy_team.active().status = Status.BRN
        elif status == "par":
            self.enemy_team.active().status = Status.PAR
        elif status == "tox":
            self.enemy_team.active().status = Status.TOX
        elif status == "slp":
            self.enemy_team.active().status = Status.SLP

    async def make_action(self, websocket):
        await senders.sendmove(websocket, self.room_id, make_best_action(self), self.turn)

    async def make_switch(self, websocket):
        await senders.sendswitch(websocket, self.room_id, make_best_switch(self)[0], self.turn)
