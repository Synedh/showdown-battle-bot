from enum import Enum
import json


class Status(Enum):
    """
    Status problem enumeration.
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
    pkm_name = pkm_name.lower().replace('-', '').replace(' ', '').replace('%', '').replace('\'', '').replace('.', '')
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


class Pokemon:
    """
    Pokemon class.
    Handle everything corresponding to it.
    """
    def __init__(self, name: str, condition: str, active: str, level: str):
        """
        Init Pokemon method.
        :param name: name of Pokemon.
        :param condition: ### TODO ###
        :param active: Bool.
        :param level: Stringified int.
        """
        self.name = name
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
            "atk": [0, 1],
            "def": [0, 1],
            "spa": [0, 1],
            "spd": [0, 1],
            "spe": [0, 1],
            "accuracy": [0, 1],
            "evasion": [0, 1]
        }

    def load_unknown(self):
        """
        Load every information of pokemon from datafiles and store them
        """
        infos = infos_for_pokemon(self.name)
        self.types = infos["types"]
        self.abilities = infos["possibleAbilities"]
        self.stats = infos["baseStats"]
        self.moves = infos["possibleMoves"]

    def load_known(self, abilities: list, item: str, _, moves: list):
        """
        Load ever information of pokemon from datafiles, but use only some of them.
        :param abilities: String. Ability of pokemon.
        :param item: String. Item of pokemon.
        :param stats: Dict. {hp, atk, def, spa, spd, spe}
        :param moves: Array. Not used.
        """
        infos = infos_for_pokemon(self.name)
        self.types = infos["types"]
        self.abilities = abilities
        self.item = item
        self.stats = infos["baseStats"]
        with open("data/moves.json", encoding='utf8') as data_file:
            json_file = json.load(data_file)
            for move in moves:
                self.moves.append(json_file[move.replace('60', '')])

    def buff_affect(self, stat: str) -> int:
        """
        Return buff corresponding to stat
        :param stat: String : ["atk", "def", "spa", "spd", "spe"]
        :return: Integer
        """
        return self.buff[stat][1]

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
        for pkm in self.pokemons:
            if pkm.active:
                return pkm
        return None

    def add(self, pokemon: Pokemon):
        """
        Add pokemon ton self.pokemons array. Exit and print error message if Team is full (6 pokemons)
        :param pokemon: Pokemon
        """
        if len(self.pokemons) < 6:
            self.pokemons.append(pokemon)
        else:
            raise IndexError("Failed to add " + pokemon.name + " : there is yet six pokemon in team :\n" + str(self))

    def remove(self, pkm_name: str):
        """
        Remove pokemon from self.pokemons array. Exit and print error message if pkm_name not present in self.pokemons
        :param pkm_name: Name of pokemon
        """
        for i, pkm in enumerate(self.pokemons):
            if pkm_name in pkm.name.lower():
                if "mega" not in pkm.name.lower():
                    del self.pokemons[i]
                return
        raise NameError("Unable to remove " + pkm_name + " from team :\n" + str(self))

    def __contains__(self, pkm_name: str) -> bool:
        return any(pkm.name == pkm_name for pkm in self.pokemons)

    def __repr__(self) -> str:
        return ', '.join([pkm.name for pkm in self.pokemons])
