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


def effi_move(move, bot_pkm, enm_pkm):
    dmg = efficiency(move["type"], enm_pkm.types) * move["basePower"]
    if move["type"] in bot_pkm.types:
        dmg *= 1.5
    return dmg


def effi_pkm(pkm1, pkm2):
    effi1 = 0
    effi2 = 0
    for move in pkm1.moves:
        dmg = effi_move(move, pkm1, pkm2)
        if effi1 < dmg:
            effi1 = dmg
    if effi1 >= 150 and pkm1.stats["spe"] - pkm2.stats["spe"] > 10:
        return effi1
    for move in pkm2.moves:
        dmg = effi_move(move, pkm2, pkm1)
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
    try:
        print("** " + best_pkm.name + " - " + str(effi))
    except TypeError:
        return None, effi
    return team.pokemons.index(best_pkm) + 1, effi


def make_best_move_test(pkm1, pkm2):
    pokemon = pkm1
    enemy_pkm = pkm2
    best_move = (None, -1)
    non_volatile_status_moves = [
        "toxic",  # tox
        "poisonpowder",  # psn
        "thunderwave", "stunspore", "glare",  # par
        "willowisp",  # brn
        "spore", "darkvoid", "sleeppowder"  # slp
    ]

    for i, move in enumerate(pokemon.moves):
        # if pokemon_moves[i]["disabled"] == True:
        #     continue
        effi = effi_move(move, pokemon, enemy_pkm)
        if move["id"] in non_volatile_status_moves and enemy_pkm.status == Status.UNK:
            effi = 100
        if effi > best_move[1]:
            best_move = (i + 1, effi)
        print("** " + move["name"] + " - " + str(effi))
    return best_move


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
        effi = effi_move(move, pokemon, enemy_pkm)
        if move["id"] in non_volatile_status_moves and enemy_pkm.status == Status.UNK:
            effi = 100
        if effi > best_move[1]:
            best_move = (i + 1, effi)
    print("** " + pokemon_moves[best_move[0] - 1]["move"] + " - " + str(best_move[1]))
    return best_move


def make_best_action(battle):
    best_enm_atk = 0
    best_bot_atk = 0
    bot_pkm = battle.bot_team.active()
    enm_pkm = battle.enemy_team.active()
    for move in bot_pkm.moves:
        effi = effi_move(move, bot_pkm, enm_pkm)
        if best_bot_atk < effi:
            best_bot_atk = effi
    for move in enm_pkm.moves:
        effi = effi_move(move, enm_pkm, bot_pkm)
        if best_enm_atk < effi:
            best_enm_atk = effi

    if bot_pkm.stats["spe"] - enm_pkm.stats["spe"] < 10 and best_enm_atk >= 150 or\
            bot_pkm.stats["spe"] - enm_pkm.stats["spe"] > 10 and best_bot_atk < 100:
        switch = make_best_switch(battle)
        if switch[1] >= effi_pkm(bot_pkm, enm_pkm):
            return "switch", switch[0]
        return "move", make_best_move(battle)[0]
    else:
        return "move", make_best_move(battle)[0]
