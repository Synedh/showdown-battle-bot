import json
from math import floor

from src.pokemon import Status


def stat_calculation(base, level, ev):
    """
    Calculation of stats based on base stat, level and ev.
    IVs are maxed, nature is not used.
    Cannot be used for HP calculation.
    :param base: Integer, base stat of wanted stat.
    :param level:  Integer, level of pokemon.
    :param ev: Integer [0, 252] quantity of ev.
    :return: Integer, actual stat.
    """
    return floor(((2 * base + 31 + floor(ev / 4)) * level) / 100 + 5)


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


def side_modificator(battle, move):
    """
    Side modificators, like screens, entry hazards, etc.
    :param battle: Battle instance
    :param move: Json object, move.
    :return: Integer [0; +oo]
    """
    if (move["category"] == "Special" and battle.screens["lightscreen"]
        or move["category"] == "Physical" and battle.screens["reflect"]):
        return 0.5
    return 1


def item_modificator(move, pkm1, pkm2):
    """
    Calculation of item modificator
    :param move: Json object, move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Integer [0; +oo[
    """
    mod = 1
    if pkm1.item == "lifeorb":
        mod *= 1.3
    elif pkm1.item == "expertbelt" and efficiency(move["type"], pkm2.types) > 1:
        mod *= 1.2
    elif pkm1.item == "choicespecs" and move["category"] == "Special":
        mod *= 1.5
    elif pkm1.item == "choiceband" and move["category"] == "Physical":
        mod *= 1.5
    elif pkm1.item == "thickclub" and move["category"] == "Physical":
        mod *= 1.5

    if pkm2.item == "airballoon" and move["type"] == "Ground":
        mod = 0
    return mod


def ability_modificator(move, pkm1, pkm2):
    """
    Calculation of ability modificator
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Integer [0; +oo[
    """
    mod = 1
    if "Tinded Lens" in pkm1.abilities and efficiency(move["type"], pkm2.types) < 1:
        mod *= 2
    elif "Guts" in pkm1.abilities and pkm1.status != Status.UNK and move["category"] == "Physical":
        mod *= 1.5

    if "Fluffy" in pkm2.abilities:
        if "contact" in move["flags"].keys():
            mod *= 0.5
        elif move["type"] == "Fire" and "contact" not in move["flags"].keys():
            mod *= 2
    elif "Solid Rock" in pkm2.abilities and efficiency(move["type"], pkm2.types) > 1:
        mod *= 0.75
    elif "Filter" in pkm2.abilities and efficiency(move["type"], pkm2.types) > 1:
        mod *= 0.75
    elif "Prism Armor" in pkm2.abilities and efficiency(move["type"], pkm2.types) > 1:
        mod *= 0.75
    elif "Levitate" in pkm2.abilities and move["type"] == "Ground":
        mod = 0
    elif "Water Absorb" in pkm2.abilities and move["type"] == "Water":
        mod = 0
    elif "Volt Absorb" in pkm2.abilities and move["type"] == "Electric":
        mod = 0
    elif "Flash Fire" in pkm2.abilities and move["type"] == "Fire":
        mod = 0
    return mod


def comparator_calculation(power, pkm1, pkm2):
    """
    Used to compare damage done by pk1 to comparative values (100, 150, etc.). Because we want exact values,
    modificators, stab, burn and efficiency are not taken into account.
    :param power: value to compare
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Integer, damage of comparative value after calculation [0, +oo[
    """
    category = ("spa", "spd") if pkm1.stats["atk"] < pkm1.stats["spa"] else ("atk", "def")
    atk = stat_calculation(pkm1.stats[category[0]], pkm1.level, 252) * pkm1.buff_affect(category[0])
    defe = stat_calculation(pkm2.stats[category[1]], pkm2.level, 0) * pkm2.buff_affect(category[1])
    return floor(((0.4 * pkm1.level + 2) * (atk / defe) * power) / 50 + 2)


def damage_calculation(battle, move, pkm1, pkm2):
    """
    Damage move calculation.
    :param battle: Battle, used for side modificator.
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Integer, damage of move [0, +oo[.
    """
    category = ("spa", "spd") if move['category'] == "Special" else ("atk", "def")
    atk = stat_calculation(pkm1.stats[category[0]], pkm1.level, 252) * pkm1.buff_affect(category[0])
    defe = stat_calculation(pkm2.stats[category[1]], pkm2.level, 0) * pkm2.buff_affect(category[1])
    stab = 1.5 if move["type"] in pkm1.types else 1
    power = move["basePower"]
    effi = efficiency(move["type"], pkm2.types)
    burn = 0.5 if pkm1.status == Status.BRN and "Guts" not in pkm1.abilities else 1
    item_mod = item_modificator(move, pkm1, pkm2)
    ability_mod = ability_modificator(move, pkm1, pkm2)
    side_mod = side_modificator(battle, move)
    return floor(floor(((0.4 * pkm1.level + 2) * (atk / defe) * power) / 50 + 2)
                 * stab * effi * burn * item_mod * ability_mod * side_mod)


def effi_boost(move, pkm1, pkm2):
    """
    Calculate if boost is worth or not. Currently only working on speed.
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Boolean, True if worth, else False
    """
    value = 0
    tmp = {}
    pkm1_spe = stat_calculation(pkm1.stats["spe"], pkm1.level, 252)
    pkm2_spe = stat_calculation(pkm2.stats["spe"], pkm2.level, 252)
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
        if (pkm1.stats["spe"] * pkm1.buff_affect("spe") - pkm2.stats["spe"] * pkm2.buff_affect("spe") < 0
                and (pkm1_spe * pkm1.buff_affect("spe") + value * pkm1_spe - pkm2_spe * pkm2.buff_affect("spe") > 0)):
            return True
    except KeyError as e:
        print("\033[31m" + str(e) + "\n" + str(tmp) + "\033[0m")
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
    :return: Integer, value of move [0, +oo[.
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
        return 60
    else:
        for pkm in team.pokemons:  # Sleep clause
            if pkm.status == Status.SLP:
                return 0
        if move["id"] in ["spore", "sleeppowder"] and "Grass" in pkm2.types \
                or "Vital Spirit" in pkm2.abilities \
                or "Insomnia" in pkm2.abilities:
            return 0
        return 200


def effi_move(battle, move, pkm1, pkm2, team):
    """
    Calculate efficiency of move based on previous functions, type, base damage and item.
    :param battle: Battle instance
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
    return damage_calculation(battle, move, pkm1, pkm2)
