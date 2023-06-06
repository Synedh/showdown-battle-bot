import json

from src.pokemon import Status


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


def effi_status(move, pkm1, pkm2, team):
    if move["id"] in ["toxic", "poisonpowder"]:
        return 100
    elif move["id"] in ["thunderwave", "stunspore", "glare"]:
        if "Electric" in pkm2.types or "Ground" in pkm2.types:
            return 0
        if pkm1.stats["spe"] - pkm2.stats["spe"] < 10:
            return 200
        return 100
    elif move["id"] == "willowisp":
        if "Fire" in pkm2.types:
            return 0
        if pkm2.stats["atk"] - pkm2.stats["spa"] > 10:
            return 200
        return 50
    else:
        for pkm in team.pokemons:  # Sleep clause
            if pkm.status == Status.SLP:
                return 0
        return 200


def effi_move(move, pkm1, pkm2, team):
    non_volatile_status_moves = [
        "toxic",  # tox
        "poisonpowder",  # psn
        "thunderwave", "stunspore", "glare",  # par
        "willowisp",  # brn
        "spore", "darkvoid", "sleeppowder", "sing", "grasswhistle", "hypnosis", "lovelykiss"  # slp
    ]

    if move["id"] in non_volatile_status_moves and pkm2.status == Status.UNK:
        return effi_status(move, pkm1, pkm2, team)
    effi = efficiency(move["type"], pkm2.types) * move["basePower"]
    if move["type"] in pkm1.types:
        effi *= 1.5
    if pkm1.item == "lifeorb":
        effi *= 1.3
    elif pkm1.item == "choicespecs" or pkm1.item == "choiceband":
        effi *= 1.5
    elif pkm1.item == "expertbelt" and efficiency(move["type"], pkm2.types) > 1:
        effi *= 1.2
    if move["type"] == "ground" and "evitate" in pkm2.abilities:
        effi = 0
    return effi


def effi_pkm(pkm1, pkm2, team):
    effi1 = 0
    effi2 = 0
    for move in pkm1.moves:
        dmg = effi_move(move, pkm1, pkm2, team)
        if effi1 < dmg:
            effi1 = dmg
    if effi1 >= 150 and pkm1.stats["spe"] - pkm2.stats["spe"] > 10:
        return effi1
    for move in pkm2.moves:
        dmg = effi_move(move, pkm2, pkm1, team)
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
        if effi_pkm(pokemon, enemy_pkm, battle.enemy_team) > effi:
            best_pkm = pokemon
            effi = effi_pkm(pokemon, enemy_pkm, battle.enemy_team)
    try:
        return team.pokemons.index(best_pkm) + 1, effi
    except ValueError:
        return None, effi


def make_best_move(battle):
    pokemon_moves = battle.current_pkm[0]["moves"]
    pokemon = battle.bot_team.active()
    enemy_pkm = battle.enemy_team.active()
    best_move = (None, -1)

    for i, move in enumerate(pokemon.moves):
        if "disabled" in pokemon_moves[i].keys() and pokemon_moves[i]["disabled"]:
            continue
        effi = effi_move(move, pokemon, enemy_pkm, battle.enemy_team)
        if effi > best_move[1]:
            best_move = (i + 1, effi)
    return best_move


def make_best_action(battle):
    best_enm_atk = 0
    best_bot_atk = 0
    bot_pkm = battle.bot_team.active()
    enm_pkm = battle.enemy_team.active()
    for move in bot_pkm.moves:
        effi = effi_move(move, bot_pkm, enm_pkm, battle.enemy_team)
        if best_bot_atk < effi:
            best_bot_atk = effi
    for move in enm_pkm.moves:
        effi = effi_move(move, enm_pkm, bot_pkm, battle.enemy_team)
        if best_enm_atk < effi:
            best_enm_atk = effi

    switch = make_best_switch(battle)
    if (switch[1] > effi_pkm(bot_pkm, enm_pkm, battle.enemy_team)
        and (best_enm_atk > 150 and bot_pkm.stats["spe"] - enm_pkm.stats["spe"] < 10
        or best_bot_atk < 100)
        and switch[0]):
        return "switch", switch[0]
    return "move", make_best_move(battle)[0]
