import json
from pokemon import Status


def efficiency(elem: str, elems: [str]):
    res = 1
    with open('data/typechart.json') as data_file:
        typechart = json.load(data_file)
    for target_elem in elems:
        tmp = typechart[target_elem]['damageTaken'][elem]
        if tmp == 1:
            res *= 2
        elif tmp == 2:
            res *= 0.5
        elif tmp == 3:
            res *= 0
    return res


def effi_move(move, pkm):
    dmg = efficiency(move["type"], pkm.types) * move["basePower"]
    if move["type"] in pkm.types:
        dmg *= 1.5
    return dmg


def effi_pkm(pkm1, pkm2):
    effi1 = 0
    effi2 = 0
    for move in pkm1.moves:
        dmg = effi_move(move, pkm2)
        if effi1 < dmg:
            effi1 = dmg
    if effi1 >= 150 and pkm1.stats["spe"] - pkm2.stats["spe"] > 10:
        return effi1
    for move in pkm2.moves:
        dmg = effi_move(move, pkm1)
        if effi2 < dmg:
            effi2 = dmg
    if effi2 >= 150 and pkm2.stats["spe"] - pkm1.stats["spe"] > 10:
        return -effi2
    return effi1 - effi2


def make_best_switch(battle):
    team = battle.bot_team
    enemy_pkm = battle.enemy_team.active()
    best_pkm = None
    effi = -1024
    for pokemon in team.pokemons:
        if pokemon == team.active() or pokemon.condition == "0 fnt":
            continue
        if effi_pkm(pokemon, enemy_pkm) > effi:
            best_pkm = pokemon
            effi = effi_pkm(pokemon, enemy_pkm)
    print(best_pkm.name)
    print(team.pokemons.index(best_pkm))
    return team.pokemons.index(best_pkm) + 1, effi


def make_best_move(battle):
    pokemon_moves = battle.current_pkm[0]["moves"]
    pokemon = battle.bot_team.active()
    enemy_pkm = battle.enemy_team.active()
    best_move = (None, -1)
    non_volatile_status_moves = [
        "toxic",  # tox
        "poisonpowder",  # psn
        "thunderwave", "stunspore", "glare",  # par
        "willowisp",  # brn
        "spore", "darkvoid", "sleeppowder"  # slp
    ]

    for i, move in enumerate(pokemon.moves):
        if pokemon_moves[i]["disabled"]:
            continue
        effi = effi_move(move, enemy_pkm)
        if move["id"] in non_volatile_status_moves and enemy_pkm.status == Status.UNK:
            effi = 100
        if effi > best_move[1]:
            best_move = (i + 1, effi)
    print(pokemon_moves[best_move[0] - 1]["id"])
    return best_move


def make_best_action(battle):
    id_move = make_best_move(battle)[0]
    return id_move
