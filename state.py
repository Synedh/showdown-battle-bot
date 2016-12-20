import json

from pokemon import Pokemon, Team


class Battle:
    def __init__(self, room_id):
        self.bot_team = Team()
        self.enemy_team = Team()
        self.current_pkm = None
        self.turn = 0
        self.room_id = room_id
        self.player_id = ""
        print("** New Battle, id : " + room_id)

    def req_loader(self, req):
        jsonobj = json.loads(req)
        self.current_pkm = jsonobj['active']
        objteam = jsonobj['side']['pokemon']

        for pkm in objteam:
            newpkm = Pokemon(pkm['details'].split(',')[0], pkm['condition'], pkm['active'])
            newpkm.load_known([pkm['baseAbility']], pkm['stats'], pkm['moves'])
            self.bot_team.add(newpkm)
        print("** Update bot_team")

    def set_player_id(self, player_id):
        self.player_id = player_id
        print("** Set bot id : " + player_id)

    def update_enemy(self, pkm_name, condition):
        print("** Update enemy : " + pkm_name)
        pass

    def makeMove(self, turn):
        print("** Start searching, turn : " + turn)
