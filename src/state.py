import json

from ia import make_best_action, make_best_switch
from pokemon import Pokemon, Team

from src import senders


class Battle:
    def __init__(self, room_id):
        self.bot_team = Team()
        self.enemy_team = Team()
        self.current_pkm = None
        self.turn = 0
        self.room_id = room_id
        self.player_id = ""

    def req_loader(self, req):
        jsonobj = json.loads(req)
        if "wait" in jsonobj.keys():
            self.turn += 1
            return
        if "forceSwitch" in jsonobj.keys():
            return
        self.current_pkm = jsonobj['active']
        objteam = jsonobj['side']['pokemon']
        self.bot_team = Team()
        for pkm in objteam:
            newpkm = Pokemon(pkm['details'].split(',')[0], pkm['condition'], pkm['active'])
            newpkm.load_known([pkm['baseAbility']], pkm['stats'], pkm['moves'])
            self.bot_team.add(newpkm)

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

    async def faint(self, websocket):
        self.bot_team.active().condition = "0 fnt"
        for pokemon in self.bot_team.pokemons:
            if pokemon.condition != "0 fnt":
                await self.make_switch(websocket)
                break

    async def make_action(self, websocket):
        self.turn += 1
        await senders.sendmove(websocket, self.room_id, make_best_action(self), self.turn)

    async def make_switch(self, websocket):
        self.turn += 1
        await senders.sendswitch(websocket, self.room_id, make_best_switch(self)[0], self.turn)
