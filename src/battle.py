import json

from src.pokemon import Stats, Pokemon, Team, Status
from src.senders import Sender
from src.ai import make_best_action, make_best_switch, make_best_move, make_best_order


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
        self.player_id = ''
        self.fields = []
        self.side_condition = []
        self.weather = ''

    def get_team(self, team_string: str) -> Team:
        """
        Return team based on team id.
        :param team_id: id of steam.
        """
        if self.player_id in team_string:
            return self.bot_team
        return self.enemy_team


    async def req_loader(self, req: str):
        """
        Parse and translate json send by server. Reload bot team. Called each turn.
        :param req: json sent by server.
        """
        jsonobj = json.loads(req)
        self.turn += 2
        self.bot_team = Team()
        for pkm in jsonobj['side']['pokemon']:
            try:
                new_pkm = Pokemon(
                    pkm['ident'].split(': ')[1],
                    pkm['details'].split(',')[0],
                    pkm['condition'],
                    pkm['active'],
                    pkm['details'].split(',')[1].split('L')[1] if len(pkm['details']) > 1 and 'L' in pkm['details'] else 100
                )
                new_pkm.load_known([pkm['baseAbility']], pkm["item"], pkm['stats'], pkm['moves'])
                self.bot_team.add(new_pkm)
            except IndexError as error:
                print(f'\033[31mIndexError: {error}\n{pkm}\033[0m')
                exit(2)
        if 'forceSwitch' in jsonobj.keys():
            await self.make_switch()
        elif 'active' in jsonobj.keys():
            self.current_pkm = jsonobj['active']

    def update_enemy(self, pkm_name: str, condition: str, pkm_variant: str = None, level: str = None):
        """
        On first turn, and each time enemy switch, update enemy team and enemy current pokemon.
        :param pkm_name: Pokemon's name
        :param condition: str current_hp/total_hp. % if enemy pkm.
        :param level: stringified int, Pokemon's level. Can be None if pokemon already exists.
        :param pkm_variant: Pokemon's variant name. Can be None if pokemon already exists.
        """
        for pkm in self.enemy_team.pokemons:
            pkm.active = False

        if pkm := next((pkm for pkm in self.enemy_team.pokemons if pkm.name == pkm_name), None):
            pkm.active = True
            pkm.condition = condition
        else:
            pkm = Pokemon(pkm_name, pkm_variant, condition, True, level)
            pkm.load_unknown()
            self.enemy_team.add(pkm)

    @staticmethod
    def update_status(pokemon, status: str = ''):
        """
        Update status problem.
        :param pokemon: Pokemon.
        :param status: String.
        """
        match status:
            case 'tox':
                pokemon.status = Status.TOX
            case 'brn':
                pokemon.status = Status.BRN
            case 'par':
                pokemon.status = Status.PAR
            case 'tox':
                pokemon.status = Status.TOX
            case 'slp':
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
        modifs = {'-6': 1/4, '-5': 2/7, '-4': 1/3, '-3': 2/5, '-2': 1/2, '-1': 2/3, '0': 1,
                  '1': 3/2, '2': 2, '3': 5/2, '4': 3, '5': 7/2, '6': 4}
        stat = next(enum_stat for enum_stat in Stats if enum_stat.value == stat)
        buff = pokemon.buff[stat][0] + quantity
        if -6 <= buff <= 6:
            pokemon.buff[stat] = [buff, modifs[str(buff)]]

    async def make_team_order(self):
        """
        Call function to correctly choose the first pokemon to send.
        :param websocket: Websocket stream.
        """
        order = ''.join([str(x[0]) for x in make_best_order(self, self.battletag.split('-')[1])])
        await self.sender.send(self.battletag, f'/team {order}', str(self.turn))

    async def make_move(self, best_move: int|None):
        """
        Call function to send move and use the sendmove sender.
        :param best_move: int: id of best move.
        """
        if not best_move:
            best_move = make_best_move(self)[0]
        await self.sender.sendmove(self.battletag, best_move, self.turn)

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
        action, value = make_best_action(self)
        match action:
            case 'move':
                await self.make_move(value)
            case 'switch':
                await self.make_switch(value)
