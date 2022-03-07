import re
import json

from src.ai import make_best_action, make_best_switch, make_best_move, make_best_order
from src.pokemon import Pokemon, Team, Status
from src.senders import Sender


class Battle:
    """
    Battle class.
    Unique for each battle.
    Handle everything concerning it.
    """
    def __init__(self, battletag: str):
        """
        init Battle method.
        :param battletag: String, battletag of battle.
        """
        self.sender = Sender()
        self.bot_team = Team()
        self.enemy_team = Team()
        self.current_pkm = None
        self.turn = 0
        self.battletag = battletag
        self.player_id = ""
        self.screens = {
            "lightscreen": False,
            "reflect": False
        }

    async def req_loader(self, req: str):
        """
        Parse and translate json send by server. Reload bot team. Called each turn.
        :param req: json sent by server.
        """
        jsonobj = json.loads(req)
        self.turn += 2
        objteam = jsonobj['side']['pokemon']
        self.bot_team = Team()
        for pkm in objteam:
            try:
                newpkm = Pokemon(
                    pkm['details'].split(',')[0],
                    pkm['condition'],
                    pkm['active'],
                    pkm['details'].split(',')[1].split('L')[1] if len(pkm['details']) > 1 and 'L' in pkm['details'] else 100
                )
                newpkm.load_known([pkm['baseAbility']], pkm["item"], pkm['stats'], pkm['moves'])
                self.bot_team.add(newpkm)
            except IndexError as error:
                print(f'\033[31mIndexError: {error}\n{pkm}\033[0m')
                exit(2)
        if "forceSwitch" in jsonobj.keys():
            await self.make_switch()
        elif "active" in jsonobj.keys():
            self.current_pkm = jsonobj["active"]

    def update_enemy(self, pkm_name: str, level: str, condition: str):
        """
        On first turn, and each time enemy switch, update enemy team and enemy current pokemon.
        :param pkm_name: Pokemon's name
        :param level: stringified int, Pokemon's level
        :param condition: str current_hp/total_hp. /100 if enemy pkm.
        """
        if "-mega" in pkm_name.lower():
            self.enemy_team.remove(pkm_name.lower().split("-mega")[0])
        if "-*" in pkm_name.lower():
            pkm_name = re.sub(r"(.+)-\*", r"\1", pkm_name)
        elif re.compile(r".+-.*").search(pkm_name.lower()):
            try:
                self.enemy_team.remove(re.sub(r"(.+)-.+", r"\1", pkm_name))
            except NameError:
                pass

        if pkm_name not in self.enemy_team:
            for pkm in self.enemy_team.pokemons:
                pkm.active = False
            pkm = Pokemon(pkm_name, condition, True, level)
            pkm.load_unknown()
            self.enemy_team.add(pkm)
        else:
            for pkm in self.enemy_team.pokemons:
                if pkm.name.lower() == pkm_name.lower():
                    pkm.active = True
                else:
                    pkm.active = False

    @staticmethod
    def update_status(pokemon, status: str = ""):
        """
        Update status problem.
        :param pokemon: Pokemon.
        :param status: String.
        """
        match status:
            case "tox":
                pokemon.status = Status.TOX
            case "brn":
                pokemon.status = Status.BRN
            case "par":
                pokemon.status = Status.PAR
            case "tox":
                pokemon.status = Status.TOX
            case "slp":
                pokemon.status = Status.SLP
            case _:
                pokemon.status = Status.UNK

    @staticmethod
    def set_buff(pokemon, stat: str, quantity: int):
        """
        Set buff to pokemon
        :param pokemon: Pokemon
        :param stat: str (len = 3)
        :param quantity: int [-6, 6]
        """
        modifs = {"-6": 1/4, "-5": 2/7, "-4": 1/3, "-3": 2/5, "-2": 1/2, "-1": 2/3, "0": 1,
                  "1": 3/2, "2": 2, "3": 5/2, "4": 3, "5": 7/2, "6": 4}
        buff = pokemon.buff[stat][0] + quantity
        if -6 <= buff <= 6:
            pokemon.buff[stat] = [buff, modifs[str(buff)]]

    async def make_team_order(self):
        """
        Call function to correctly choose the first pokemon to send.
        :param websocket: Websocket stream.
        """
        order = "".join([str(x[0]) for x in make_best_order(self, self.battletag.split('-')[1])])
        await self.sender.send(self.battletag, "/team " + order + "|" + str(self.turn))

    async def make_move(self, best_move: list[int] = None):
        """
        Call function to send move and use the sendmove sender.
        :param websocket: Websocket stream.
        :param best_move: [int, int] : [id of best move, value].
        """
        if not best_move:
            best_move = make_best_move(self)
        if best_move[1] < 20:
            print("Best move power < 20. Move list : "
                  + ", ".join([move["move"] for move in self.current_pkm[0]['moves']]) + ".")
        if "canMegaEvo" in self.current_pkm[0]:
            await self.sender.sendmove(self.battletag, str(best_move[0]) + " mega", self.turn)
        else:
            await self.sender.sendmove(self.battletag, best_move[0], self.turn)

    async def make_switch(self, best_switch=None):
        """
        Call function to send swich and use the sendswitch sender.
        :param websocket: Websocket stream.
        :param best_switch: int, id of pokemon to switch.
        """
        if not best_switch:
            best_switch = make_best_switch(self)[0]
        await self.sender.sendswitch(self.battletag, best_switch, self.turn)

    async def make_action(self):
        """
        Launch best action chooser and call corresponding functions.
        :param websocket: Websocket stream.
        """
        action = make_best_action(self)
        if action[0] == "move":
            await self.make_move(action[1:])
        if action[0] == "switch":
            await self.make_switch(action[1])
