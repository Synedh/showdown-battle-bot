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
    pkm_name = pkm_name.lower().replace('-', '').replace(' ', '').replace('%', '').replace('\'', '').replace('.', '')
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
        self.moves = infos["possibleMoves"]

    def load_known(self, abilities, stats, moves):
        stats == stats
        infos = infos_for_pokemon(self.name)
        self.types = infos["types"]
        self.abilities = abilities
        self.stats = infos["baseStats"]
        with open("data/moves.json") as data_file:
            json_file = json.load(data_file)
            for move in moves:
                self.moves.append(json_file[move.replace('60', '')])

    def update(self, status, active):
        self.status = status
        self.active = active

    def __repr__(self):
        return str(vars(self))


class Team:
    def __init__(self, *pkms):
        self.pokemons = []
        for pkm in pkms:
            self.add(pkm)

    def active(self):
        for pkm in self.pokemons:
            if pkm.active:
                return pkm
        return None

    def add(self, pokemon):
        if len(self.pokemons) < 6:
            self.pokemons.append(pokemon)
        else:
            print("Error : Failed to add " +  pokemon.name + " : there is yet six pokemon in the team :")
            print(self)
            exit()

    def remove(self, pkm_name):
        for pkm in self.pokemons:
            if pkm.name == pkm_name:
                self.pokemons.remove(pkm)
                return
        print("Error : Unable to remove " + pkm_name + " from team :")
        print(self)
        exit()

    def __contains__(self, pkm_name: str):
        return any(pkm.name == pkm_name for pkm in self.pokemons)
        # for pkm in self.pokemons:
        #     if pkm.name == pkm_name:
        #         return True
        # return False

    def __repr__(self):
        res = ""
        for pkm in self.pokemons:
            res += str(pkm.name) + "\n"
        return res
