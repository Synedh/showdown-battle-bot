import json
from pokemon import Status

def efficiency(elem, elems):
    res = 1
    elem1 = elems[0]
    elem2 = elems[1] if len(elems) > 1 else None
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

def make_best_switch(battle):
    pass

def make_best_move(battle):
    pokemon_moves = battle.current_pkm[0]["moves"]
    pokemon = battle.bot_team.active()
    enemy_pkm = battle.enemy_team.active()
    best_move = (None, -1)
    nonVolatileStatusMoves = [
        "toxic", # tox
        "poisonpowder", # psn
        "thunderwave", "stunspore", "glare", # par
        "willowisp", # brn
        "spore", "darkvoid", "sleeppowder" # slp
    ]

    for i, move in enumerate(pokemon.moves):
        if pokemon_moves[i]["disabled"] == "true":
            continue
        effi = efficiency(move["type"], enemy_pkm.types)
        if move["type"] in pokemon.types:
            effi *= 1.5
        if move["id"] in nonVolatileStatusMoves and enemy_pkm.status == Status.UNK:
            effi = 100
        if effi * move["basePower"] > best_move[1]:
            best_move = (i, effi * move["basePower"])
    print(pokemon_moves[best_move[0]]["id"])
    return best_move[0] + 1

def make_best_action(battle):
    id_move = make_best_move(battle)
    return id_move