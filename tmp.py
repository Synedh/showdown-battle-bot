#coding: utf8

import json

def efficiency(elem, elem1, elem2=None):
    res = 1
    with open('data/typechart.json') as data_file:
        typechart = json.load(data_file)
    tmp = typechart[elem1]['damageTaken'][elem]
    if tmp == 1:
        res *= 2
    elif tmp == 2:
        res *= 0.5
    elif tmp == 3:
        res *= 0
    if elem2:
        tmp = typechart[elem2]['damageTaken'][elem]
        if tmp == 1:
            res *= 2
        elif tmp == 2:
            res *= 0.5
        elif tmp == 3:
            res *= 0
    return res

def infos_for_pokemon(pkmName):
    res = {
        "types": [],
        "possibleAbilities": [],
        "baseStats": {},
        "possibleMoves": []
    }
    with open('data/pokedex.json') as data_file:
        pokemon = json.load(data_file)[pkmName.lower()]
    res["types"] = pokemon["types"]
    res["possibleAbilities"] = list(pokemon["abilities"].values())
    res["baseStats"] = pokemon["baseStats"]
    with open('data/formats-data.json') as data_file:
        pokemon_moves = json.load(data_file)[pkmName.lower()]["randomBattleMoves"]
    with open("data/moves.json") as data_file:
        moves = json.load(data_file)
    for move in pokemon_moves:
        res["possibleMoves"].append(moves[move])
    return res

print(str(infos_for_pokemon("skarmory")))