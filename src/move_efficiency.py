import json

from src.pokemon import Status


def stat_calculation(base, level):
    """
    Calculation of stats based on base stat and level.
    IV and EV are maxed, nature is not used.
    Cannot be used for HP calculation.
    :param base: Integer, base stat of wanted stat
    :param level:  Integer, level of pokemon
    :return: Integer, actual stat
    """
    return int(abs(((2 * base + 31 + 63) * level) / 100 + 5))


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


def damage_calculation(move, pkm1, pkm2):
    """
    Damage move calculation.
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Integer, damage of move [0, +oo].
    """
    category = ("spa", "spd") if move['category'] == "Special" else ("atk", "def")
    atk = stat_calculation(pkm1.stats[category[0]], pkm1.level) * pkm1.buff_affect(category[0])
    defe = stat_calculation(pkm2.stats[category[1]], pkm2.level) * pkm2.buff_affect(category[1])
    stab = 1.5 if move["type"] in pkm1.types else 1
    power = move["basePower"]
    effi = efficiency(move["type"], pkm2.types)
    mod1 = 0.5 if pkm1.status == Status.BRN else 1
    mod2 = 1.3 if pkm1.item == "lifeorb" else 1
    mod3 = 1.2 if pkm1.item == "expertbelt" and effi > 1 else 1
    print("((((((((" + str(pkm1.level) + " * 2 / 5) + 2) * " + str(power) + " * " + str(atk) + " / 50) / "
          + str(defe) + ") * " + str(mod1) + ") / 2) * " + str(mod2) + ") * " + str(stab) + " * " + str(effi)
          + " * " + str(mod3) + ")")
    return ((((((((pkm1.level * 2 / 5) + 2) * power * atk / 50) / defe) * mod1) / 2) * mod2) * stab * effi * mod3)


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
        elif ("secondary" in tmp and tmp["secondary"] and "self" in tmp["secondary"]
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

    effi = damage_calculation(move, pkm1, pkm2)

    # effi = efficiency(move["type"], pkm2.types) * move["basePower"]
    # if move["type"] in pkm1.types:
    #     effi *= 1.5
    # if pkm1.item == "lifeorb":
    #     effi *= 1.3
    # elif pkm1.item == "choicespecs" or pkm1.item == "choiceband":
    #     effi *= 1.5
    # elif pkm1.item == "expertbelt" and efficiency(move["type"], pkm2.types) > 1:
    #     effi *= 1.2
    # elif pkm1.item == "thickclub":
    #     effi *= 2
    #
    # if move["category"] == "Special":
    #     effi *= pkm1.buff_affect("spa") / pkm2.buff_affect("spd")
    # elif move["category"] == "Physical":
    #     effi *= pkm1.buff_affect("atk") / pkm2.buff_affect("def")
    return effi
