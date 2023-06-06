from enum import Enum
import json


class Status(Enum):
    PSN = 0
    TOX = 1
    PAR = 2
    BRN = 3
    SLP = 4
    FRZ = 5


def infos_for_pokemon(pkm_name):
    res = {
        "types": [],
        "possibleAbilities": [],
        "baseStats": {},
        "possibleMoves": []
    }
    with open('data/pokedex.json') as data_file:
        pokemon = json.load(data_file)[pkm_name.lower()]
    res["types"] = pokemon["types"]
    res["possibleAbilities"] = list(pokemon["abilities"].values())
    res["baseStats"] = pokemon["baseStats"]
    with open('data/formats-data.json') as data_file:
        pokemon_moves = json.load(data_file)[pkm_name.lower()]["randomBattleMoves"]
    with open("data/moves.json") as data_file:
        moves = json.load(data_file)
    for move in pokemon_moves:
        res["possibleMoves"].append(moves[move])
    return res


class Pokemon:
    def __init__(self, name, condition, active):
        self.name = name
        self.condition = condition
        self.status = ""
        self.active = active
        self.types = []
        self.abilities = []
        self.stats = {}
        self.moves = []

    def load_unknown(self):
        infos = infos_for_pokemon(self.name)
        self.types = infos["types"]
        self.abilities = infos["possibleAbilities"]
        self.stats = infos["baseStats"]
        self.moves = ["possibleMoves"]

    def load_known(self, types, abilities, stats, moves):
        self.types = types
        self.abilities = abilities
        self.stats = stats
        self.moves = moves

    def set_status(self, status):
        self.status = status
