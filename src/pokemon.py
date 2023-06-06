import re
import json
from enum import Enum
from math import floor

class Status(Enum):
    """
    Status changes.
    """
    UNK = 0
    PSN = 1
    TOX = 2
    PAR = 3
    BRN = 4
    SLP = 5
    FRZ = 6


class Stats(Enum):
    """
    Pokemon stats
    """
    HP = 'hp'
    ATK = 'atk'
    DEF = 'def'
    SPA = 'spa'
    SPD = 'spd'
    SPE = 'spe'
    ACCURACY = 'accuracy'
    EVASION = 'evasion'


def infos_for_pokemon(pkm_name: str) -> dict:
    """
    Filtrate, regroup and translate data from json files.
    :param pkm_name: Pokemon's name
    :return: Dict. {types, possibleAbilities, baseStats, possibleMoves}
    """
    pkm_name = re.sub(r'\W', '', pkm_name.lower())
    res = {
        "types": [],
        "possibleAbilities": [],
        "baseStats": {},
        "possibleMoves": []
    }
    with open('data/pokedex.json', encoding='utf8') as data_file:
        pokemon = json.load(data_file)[pkm_name]
    res["types"] = pokemon["types"]
    res["possibleAbilities"] = list(pokemon["abilities"].values())
    res["baseStats"] = pokemon["baseStats"]
    with open('data/formats-data.json', encoding='utf8') as data_file:
        try:
            pokemon_moves = json.load(data_file)[pkm_name]["randomBattleMoves"]
        except KeyError:
            pokemon_moves = []
    with open("data/moves.json", encoding='utf-8') as data_file:
        moves = json.load(data_file)
    for move in pokemon_moves:
        res["possibleMoves"].append(moves[move])
    return res


def stat_calculation(base, level, ev, hp=False):
    """
    Calculation of stats based on base stat, level and ev.
    IVs are maxed, nature is not used.
    Cannot be used for HP calculation.
    :param base: Integer, base stat of wanted stat.
    :param level:  Integer, level of pokemon.
    :param ev: Integer [0, 252] quantity of ev.
    :param hp: bool, True if stat is heal points. Default False.
    :return: Integer, actual stat.
    """
    if hp:
        return floor(((2 * base + 31 + floor(ev / 4)) * level) / 100 + 10)
    return floor(((2 * base + 31 + floor(ev / 4)) * level) / 100 + 5)


class Pokemon:
    """
    Pokemon class.
    Handle everything corresponding to it.
    """
    def __init__(self, name: str, variant: str, condition: str, active: bool, level: str):
        """
        Init Pokemon method.
        :param name: name of Pokemon.
        :param condition: current life of pokemon ## TODO ##
        :param active: bool, True if pokemon is currently fighting
        :param level: Stringified int.
        """
        self.name = name
        self.variant = variant
        self.condition = condition
        self.status = Status.UNK
        self.active = active
        self.level = int(level)
        self.types = []
        self.item = ""
        self.abilities = []
        self.stats = {}
        self.moves = []
        self.buff = {
            Stats.ATK: [0, 1],
            Stats.DEF: [0, 1],
            Stats.SPA: [0, 1],
            Stats.SPD: [0, 1],
            Stats.SPE: [0, 1],
            Stats.ACCURACY: [0, 1],
            Stats.EVASION: [0, 1]
        }

    def load_unknown(self):
        """
        Load every information of pokemon from datafiles and store them
        """
        try:
            infos = infos_for_pokemon(self.variant)
        except KeyError:
            infos = infos_for_pokemon(self.name)
        self.types = infos["types"]
        self.abilities = infos["possibleAbilities"]
        self.stats = {
            Stats.HP: infos["baseStats"]['hp'],
            Stats.ATK: infos["baseStats"]['atk'],
            Stats.DEF: infos["baseStats"]['def'],
            Stats.SPA: infos["baseStats"]['spa'],
            Stats.SPD: infos["baseStats"]['spd'],
            Stats.SPE: infos["baseStats"]['spe']
        }
        self.moves = infos["possibleMoves"]

    def load_known(self, abilities: list, item: str, _, moves: list):
        """
        Load ever information of pokemon from datafiles, but use only some of them.
        :param abilities: String. Ability of pokemon.
        :param item: String. Item of pokemon.
        :param stats: Dict. {hp, atk, def, spa, spd, spe}
        :param moves: Array. Not used.
        """
        try:
            infos = infos_for_pokemon(self.variant)
        except KeyError:
            infos = infos_for_pokemon(self.name)
        self.types = infos["types"]
        self.abilities = abilities
        self.item = item
        self.stats = {
            Stats.ATK: infos['baseStats']['atk'],
            Stats.DEF: infos['baseStats']['def'],
            Stats.SPA: infos['baseStats']['spa'],
            Stats.SPD: infos['baseStats']['spd'],
            Stats.SPE: infos['baseStats']['spe']
        }
        with open('data/moves.json', encoding='utf8') as data_file:
            json_file = json.load(data_file)
            for move in moves:
                self.moves.append(json_file[move.replace('60', '')])

    def buff_affect(self, stat: Stats) -> int:
        """
        Return buff corresponding to stat
        :param stat: Stats
        :return: Integer
        """
        return self.buff[stat][1]

    def compute_stat(self, stat: Stats, ev: int = 252) -> int:
        """
        Return calculated stats after modificators
        :param stat: Stats
        :return: Integer
        """
        return stat_calculation(self.stats[stat], self.level, ev) * self.buff_affect(stat)

    def __repr__(self) -> int:
        return str(vars(self))


class Team:
    """
    Team class.
    Contain pokemon list.
    """
    def __init__(self, *pkms: list[Pokemon]):
        """
        init Team method
        :param pkms: Array of pokemons. Can be empty, Cannot contain more than six pokemon.
        """
        self.pokemons = []
        for pkm in pkms:
            self.add(pkm)

    def active(self) -> Pokemon|None:
        """
        Return active pokemon of Team
        :return: Pokemon
        """
        return next((pkm for pkm in self.pokemons if pkm.active), None)

    def add(self, pokemon: Pokemon):
        """
        Add pokemon ton self.pokemons array.
        Exit and print error message if Team is full (6 pokemons)
        :param pokemon: Pokemon
        """
        if len(self.pokemons) >= 6:
            raise IndexError(f'Failed to add {pokemon.name}: team is full :\n{self}')
        self.pokemons.append(pokemon)

    def remove(self, pkm_name: str):
        """
        Remove pokemon from self.pokemons array.
        Exit and print error message if pkm_name not present in self.pokemons
        :param pkm_name: Name of pokemon
        """
        for i, pkm in enumerate(self.pokemons):
            if pkm_name == pkm.name:
                del self.pokemons[i]
                break
        else:
            raise ValueError(f'Unable to remove {pkm_name} from team :\n{self}')

    def __contains__(self, pkm_name: str) -> bool:
        return any(pkm.name == pkm_name for pkm in self.pokemons)

    def __repr__(self) -> str:
        return ', '.join(pkm.name for pkm in self.pokemons)
