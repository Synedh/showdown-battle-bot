import json

from src.pokemon import Status


def efficiency(elem: str, elems: [str]):
    """
    Type chart calculator.
    :param elem: Elem of move.
    :param elems: Elements of target pokemon.
    :return: Integer, efficiency multiplication.
    """
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


def effi_boost(move, pkm1, pkm2):
    value = 0
    tmp = {}
    for i in pkm1.moves:
        if i["name"] == move["move"]:
            tmp = i
    try:
        if "boosts" in tmp and "spe" in tmp["boosts"]:
            value = tmp["boosts"]["spe"]
        elif "self" in tmp and "boosts" in tmp["self"] and "spe" in tmp["self"]["boosts"]:
            value = tmp["self"]["boosts"]["spe"]
        elif ("secondary" in tmp and  tmp["secondary"] and "self" in tmp["secondary"]
              and "boosts" in tmp["secondary"]["self"] and "spe" in tmp["secondary"]["self"]["boosts"]):
            value = tmp["secondary"]["self"]["boosts"]["spe"]
        if (pkm1.stats["spe"] * pkm1.buff_affect("spe") - pkm2.stats["spe"] * pkm2.buff_affect("spe") < 10
            and (pkm1.stats["spe"] * pkm1.buff_affect("spe") + value * pkm1.stats["spe"]
                 - pkm2.stats["spe"] * pkm2.buff_affect("spe") > 10)):
            return True
    except KeyError as e:
        print("\033[31m" + str(e))
        print(str(tmp) + "\033[0m")
        exit()
    return False


def effi_status(move, pkm1, pkm2, team):
    """
    Efficiency status calculator.
    Give arbitrary value to status move depending on types, abilities and stats.
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move
    :param pkm2: Pokemon that will receive move
    :param team: Team of pkm1
    :return: Integer, value of move [0, +oo].
    """
    if move["id"] in ["toxic", "poisonpowder"]:
        if "Poison" in pkm2.types or "Steel" in pkm2.types:
            return 0
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
        if move["id"] in ["spore", "sleeppowder"] and "Grass" in pkm2.types \
                or "Vital Spirit" in pkm2.abilities \
                or "Insomnia" in pkm2.abilities:
            return 0
        return 200


def effi_move(move, pkm1, pkm2, team):
    """
    Calculate efficiency of move based on previous functions, type, base damage and item.
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move
    :param pkm2: Pokemon that will receive move
    :param team: Team of pkm1
    :return: Integer
    """
    non_volatile_status_moves = [
        "toxic",  # tox
        "poisonpowder",  # psn
        "thunderwave", "stunspore", "glare",  # par
        "willowisp",  # brn
        "spore", "darkvoid", "sleeppowder", "sing", "grasswhistle", "hypnosis", "lovelykiss"  # slp
    ]

    if move["id"] in non_volatile_status_moves and pkm2.status == Status.UNK:
        return effi_status(move, pkm1, pkm2, team)

    if (move["type"] == "Ground" and ("Levitate" in pkm2.abilities or pkm2.item == "Air Balloon")
        or move["type"] == "Water" and "Water Absorb" in pkm2.abilities
            or move["type"] == "Electric" and "Volt Absorb" in pkm2.abilities):
        return 0

    effi = efficiency(move["type"], pkm2.types) * move["basePower"]
    if move["type"] in pkm1.types:
        effi *= 1.5
    if pkm1.item == "lifeorb":
        effi *= 1.3
    elif pkm1.item == "choicespecs" or pkm1.item == "choiceband":
        effi *= 1.5
    elif pkm1.item == "expertbelt" and efficiency(move["type"], pkm2.types) > 1:
        effi *= 1.2
    elif pkm1.item == "thickclub":
        effi *= 2

    if move["category"] == "Special":
        effi *= pkm1.buff_affect("spa") / pkm2.buff_affect("spd")
    elif move["category"] == "Physical":
        effi *= pkm1.buff_affect("atk") / pkm2.buff_affect("def")
    return effi


def effi_pkm(pkm1, pkm2, team):
    """
    Efficiency of pokemon against other.
    Based on previous function.
    If efficiency of a pokemon > 150 and is faster, efficiency of the other pokemon is not taken.
    effi_pkm(a, b, team_a) = - effi_pkm(b, a, team_b)
    :param pkm1: Pokemon that will use move
    :param pkm2: Pokemon that will receive move
    :param team: Team of pkm1
    :return: Integer, can be negative.
    """
    effi1 = 0
    effi2 = 0
    for move in pkm1.moves:
        dmg = effi_move(move, pkm1, pkm2, team)
        if effi1 < dmg:
            effi1 = dmg
    if effi1 >= 150 and pkm1.stats["spe"] * pkm1.buff_affect("spe") - pkm2.stats["spe"] * pkm2.buff_affect("spe") > 10:
        return effi1
    for move in pkm2.moves:
        dmg = effi_move(move, pkm2, pkm1, team)
        if effi2 < dmg:
            effi2 = dmg
    if effi2 >= 150 and pkm2.stats["spe"] * pkm1.buff_affect("spe") - pkm1.stats["spe"] * pkm2.buff_affect("spe") > 10:
        return -effi2
    return effi1 - effi2


def make_best_switch(battle):
    """
    Parse battle.bot_tem to find the best pokemon based on his efficiency against current enemy pokemon.
    :param battle: Battle object, current battle.
    :return: {Index of pokemon in bot_team (Integer, [-1, 6]), efficiency (Integer, [0, +oo])}
    """
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
        return -1, -1024


def make_best_move(battle):
    """
    Parse attacks of current pokemon and send the most efficient based on previous function
    :param battle: Battle object, current battle.
    :return: {Index of move in pokemon (Integer, [-1, 4), efficiency (Integer, [0, +oo])}
    """
    pokemon_moves = battle.current_pkm[0]["moves"]
    pokemon = battle.bot_team.active()
    enemy_pkm = battle.enemy_team.active()
    best_move = (None, -1)

    if len(pokemon_moves) == 1:  # Case Outrage, Mania, Phantom Force, etc.
        for move in pokemon.moves:
            if move["name"] == pokemon_moves[0]["move"]:
                return 1, effi_move(move, pokemon, enemy_pkm, battle.enemy_team)

    for i, move in enumerate(pokemon.moves):  # Classical parse
        if "disabled" in pokemon_moves[i].keys() and pokemon_moves[i]["disabled"]:
            continue
        effi = effi_move(move, pokemon, enemy_pkm, battle.enemy_team)
        if effi > best_move[1]:
            best_move = (i + 1, effi)

    for i, move in enumerate(pokemon_moves):  # Boosts handling
        if effi_boost(move, pokemon, enemy_pkm):
            best_move = (i + 1, best_move[1] + 1)
    return best_move


def make_best_action(battle):
    """
    Global function to choose best action to do each turn.
    Select best action of bot and enemy pokemon, then best pokemon to switch. And finally, chose if it worth or not to
    switch.
    :param battle: Battle object, current battle.
    :return: {Index of move in pokemon (["move"|"switch"], Integer, [-1, 6])}
    """
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
        and (best_enm_atk > 150
             and (bot_pkm.stats["spe"] * bot_pkm.buff_affect("spe")
                  - enm_pkm.stats["spe"] * bot_pkm.buff_affect("spe")) < 10
             or best_bot_atk < 100) and switch[0]):
        return "switch", switch[0]
    return "move", make_best_move(battle)[0]
