import json

from src.ia import make_best_action, make_best_switch, make_best_move
from src.pokemon import Pokemon, Team, Status
from src import senders


class Battle:
    """
    Battle class.
    Unique for each battle.
    Handle everything concerning it.
    """
    def __init__(self, battletag):
        """
        init Battle method.
        :param room_id: Id of battle.
        """
        self.bot_team = Team()
        self.enemy_team = Team()
        self.current_pkm = None
        self.turn = 0
        self.battletag = battletag
        self.player_id = ""

    async def req_loader(self, req, websocket):
        """
        Parse and translate json send by server. Reload bot team. Called each turn.
        :param req: json sent by server.
        :param websocket: Websocket stream.
        """
        jsonobj = json.loads(req)
        self.turn += 1
        objteam = jsonobj['side']['pokemon']
        self.bot_team = Team()
        for pkm in objteam:
            newpkm = Pokemon(pkm['details'].split(',')[0], pkm['condition'], pkm['active'])
            newpkm.load_known([pkm['baseAbility']], pkm["item"], pkm['stats'], pkm['moves'])
            self.bot_team.add(newpkm)
        if "forceSwitch" in jsonobj.keys():
            await self.make_switch(websocket)
        elif "active" in jsonobj.keys():
            self.current_pkm = jsonobj["active"]

    def set_player_id(self, player_id):
        """
        Set player's id
        :param player_id: Player's id.
        """
        self.player_id = player_id

    def update_enemy(self, pkm_name, condition):
        """
        On first turn, and each time enemy switch, update enemy team and enemy current pokemon.
        :param pkm_name: Pokemon's name
        :param condition: ### TODO ###
        """
        if "mega" in pkm_name.lower():
            self.enemy_team.remove(pkm_name.lower().split("-mega")[0])

        if pkm_name not in self.enemy_team:
            for pkm in self.enemy_team.pokemons:
                pkm.active = False
            pkm = Pokemon(pkm_name, condition, True)
            pkm.load_unknown()
            self.enemy_team.add(pkm)
        else:
            for pkm in self.enemy_team.pokemons:
                if pkm.name.lower() == pkm_name.lower():
                    pkm.active = True
                else:
                    pkm.active = False

    def update_status_enemy(self, status):
        """
        Update status problem.
        :param status: String.
        """
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

    def set_enemy_item(self, item):
        """
        Set enemy item.
        :param item: Item string.
        """
        self.enemy_team.active().item = item

    async def make_move(self, wensocket):
        """
        Call function to send move and use the sendmove sender.
        :param wensocket: Websocket stream.
        """
        if "canMegaEvo" in self.current_pkm[0]:
            await senders.sendmove(wensocket, self.battletag, str(make_best_move(self)[0]) + " mega", self.turn)
        else:
            await senders.sendmove(wensocket, self.battletag, make_best_move(self)[0], self.turn)

    async def make_switch(self, websocket):
        """
        Call function to send swich and use the sendswitch sender.
        :param wensocket: Websocket stream.
        """
        await senders.sendswitch(websocket, self.battletag, make_best_switch(self)[0], self.turn)

    async def make_action(self, websocket):
        """
        Launch best action chooser and call corresponding functions.
        :param websocket: Websocket stream.
        """
        action = make_best_action(self)
        if action[0] == "move":
            await self.make_move(websocket)
        if action[0] == "switch":
            await self.make_switch(websocket)
