from enum import Enum
import json


class Status(Enum):
    UNK = 0
    PSN = 1
    TOX = 2
    PAR = 3
    BRN = 4
    SLP = 5
    FRZ = 6


def infos_for_pokemon(pkm_name):
    pkm_name = pkm_name.lower()
    if "rotom" in pkm_name or "wormadam" in pkm_name or "lycanroc" in pkm_name or "arceus" in pkm_name or "alola" in pkm_name:
        pkm_name = pkm_name.split('-')[0] + pkm_name.split('-')[1]
    res = {
        "types": [],
        "possibleAbilities": [],
        "baseStats": {},
        "possibleMoves": []
    }
    with open('data/pokedex.json') as data_file:
        pokemon = json.load(data_file)[pkm_name]
    res["types"] = pokemon["types"]
    res["possibleAbilities"] = list(pokemon["abilities"].values())
    res["baseStats"] = pokemon["baseStats"]
    with open('data/formats-data.json') as data_file:
        pokemon_moves = json.load(data_file)[pkm_name]["randomBattleMoves"]
    with open("data/moves.json") as data_file:
        moves = json.load(data_file)
    for move in pokemon_moves:
        res["possibleMoves"].append(moves[move])
    return res


class Pokemon:
    def __init__(self, name, condition, active):
        self.name = name
        self.condition = condition
        self.status = Status.UNK
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

    def load_known(self, abilities, stats, moves):
        self.types = infos_for_pokemon(self.name)["types"]
        self.abilities = abilities
        self.stats = stats
        self.moves = moves

    def set_status(self, status):
        self.status = status

class Team:
    def __init__(self, p1=None, p2=None, p3=None, p4=None, p5=None, p6=None):
        self.pokemons = []
        if p1: self.pokemons.append(p1)
        if p2: self.pokemons.append(p2)
        if p3: self.pokemons.append(p3)
        if p4: self.pokemons.append(p4)
        if p5: self.pokemons.append(p5)
        if p6: self.pokemons.append(p6)

    def add(self, pokemon):
        if len(self.pokemons) < 6:
            self.pokemons.append(pokemon)
        else:
            print("Error : There is yet six pokemon in the team")
            exit()
    def __repr__(self):
        for pkm in self.pokemons:
            print(vars(pkm))