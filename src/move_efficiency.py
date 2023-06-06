import json
from math import floor

from src.pokemon import Status, Stats, Pokemon, Team, stat_calculation


def efficiency(elem: str, elems: list[str]) -> int:
    """
    Type chart calculator.
    :param elem: Elem of move.
    :param elems: Elements of target pokemon.
    :return: Integer, efficiency multiplication.
    """
    res = 1
    with open('data/typechart.json', encoding='utf8') as data_file:
        typechart = json.load(data_file)
        for target_elem in elems:
            tmp = typechart[target_elem.lower()]['damageTaken'][elem]
            res *= {0: 1, 1: 2, 2: 0.5, 3: 0}[tmp]
    return res


def item_modificator(move: dict, pkm1: Pokemon, pkm2: Pokemon) -> float|int:
    """
    Calculation of item modificator
    :param move: Json object, move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Float or Integer [0; +oo[
    """
    mod = 1
    if pkm1.item == 'lifeorb':
        mod *= 1.3
    elif pkm1.item == 'expertbelt' and efficiency(move['type'], pkm2.types) > 1:
        mod *= 1.2
    elif pkm1.item == 'choicespecs' and move['category'] == 'Special':
        mod *= 1.5
    elif pkm1.item == 'choiceband' and move['category'] == 'Physical':
        mod *= 1.5
    elif pkm1.item == 'thickclub' and move['category'] == 'Physical':
        mod *= 1.5
    if pkm2.item == 'airballoon' and move['type'] == 'Ground':
        mod = 0
    return mod


def ability_modificator(move: dict, pkm1: Pokemon, pkm2: Pokemon) -> float|int:
    """
    Calculation of ability modificator
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Float or Integer [0; +oo[
    """
    mod = 1
    if 'Tinded Lens' in pkm1.abilities and efficiency(move['type'], pkm2.types) < 1:
        mod *= 2
    if 'Guts' in pkm1.abilities and pkm1.status != Status.UNK and move['category'] == 'Physical':
        mod *= 1.5

    if 'Fluffy' in pkm2.abilities:
        if 'contact' in move['flags'].keys():
            mod *= 0.5
        elif move['type'] == 'Fire' and 'contact' not in move['flags'].keys():
            mod *= 2
    if 'Solid Rock' in pkm2.abilities and efficiency(move['type'], pkm2.types) > 1:
        mod *= 0.75
    if 'Filter' in pkm2.abilities and efficiency(move['type'], pkm2.types) > 1:
        mod *= 0.75
    if 'Prism Armor' in pkm2.abilities and efficiency(move['type'], pkm2.types) > 1:
        mod *= 0.75
    if 'Levitate' in pkm2.abilities and move['type'] == 'Ground':
        mod = 0
    if 'Water Absorb' in pkm2.abilities and move['type'] == 'Water':
        mod = 0
    if 'Volt Absorb' in pkm2.abilities and move['type'] == 'Electric':
        mod = 0
    if 'Flash Fire' in pkm2.abilities and move['type'] == 'Fire':
        mod = 0
    if 'Prankster' in pkm1.abilities and move['priority'] > 0 and 'Dark' in pkm2.types:
        mod = 0
    return mod


def field_modificator(battle, move: dict, _: Pokemon, pkm2: Pokemon) -> float|int:
    """
    Calculation of fields modificator (terrains, weather, screens, ...)
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Float or Integer [0; +oo[
    """
    mod = 1
    if 'Electric Terrain' in battle.fields and move['type'] == 'Electric':
        mod *= 1.3
    if 'Grassy Terrain' in battle.fields and move['type'] == 'Grass':
        mod *= 1.3
    if 'Misty Terrain' in battle.fields and move['type'] == 'Dragon' and 'Fly' not in pkm2.types:
        mod *= 0.5
    if 'Psychic Terrain' in battle.fields and move['type'] == 'Psychic':
        mod *= 1.3
    if 'Psychic Terrain' in battle.fields and move['priority'] > 0:
        return 0

    if (battle.weather.lower() == 'Rain' and move['type'] == 'Water'
        or battle.weather.lower() == 'Sunny' and move['type'] == 'Fire'):
        mod *= 1.5

    if (battle.weather.lower() == 'Rain' and move['type'] == 'Fire'
        or battle.weather.lower() == 'Sunny' and move['type'] == 'Water'):
        mod *= 0.5

    if (move['category'] == 'Special' and battle.screens['lightscreen']
        or move['category'] == 'Physical' and battle.screens['reflect']):
        mod *= 0.5
    return mod


def comparator_calculation(power: float|int, pkm1: Pokemon, pkm2: Pokemon) -> int:
    """
    Used to compare damage done by pk1 to comparative values (100, 150, etc.).
    Because we want exact values, modificators, stab, burn and efficiency are
    not taken into account.
    :param power: value to compare
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Integer, damage of comparative value after calculation [0, +oo[
    """
    categories = Stats.SPA, Stats.SPD
    if pkm1.stats[Stats.ATK] > pkm1.stats[Stats.SPA]:
        categories = Stats.ATK, Stats.DEF
    atk = pkm1.compute_stat(categories[0])
    defe = pkm2.compute_stat(categories[1], 0)
    return floor(((0.4 * pkm1.level + 2) * (atk / defe) * power) / 50 + 2)


def damage_calculation(battle, move: dict, pkm1: Pokemon, pkm2: Pokemon) -> int:
    """
    Damage move calculation.
    :param battle: Battle, used for side modificator.
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Integer, damage of move [0, +oo[.
    """
    if move['name'] == 'Seismic Toss' and 'Ghost' not in pkm2.types:
        return pkm1.level
    categories = (Stats.SPA, Stats.SPD) if move['category'] == 'Special' else (Stats.ATK, Stats.DEF)
    atk = pkm1.compute_stat(categories[0])
    defe = pkm2.compute_stat(categories[1], 0)
    power = move['basePower']
    stab = 1.5 if move['type'] in pkm1.types else 1
    effi = efficiency(move['type'], pkm2.types)
    burn = 0.5 if pkm1.status == Status.BRN and move['category'] == 'Physical' and 'Guts' not in pkm1.abilities else 1
    item_mod = item_modificator(move, pkm1, pkm2)
    ability_mod = ability_modificator(move, pkm1, pkm2)
    field_mod = field_modificator(battle, move, pkm1, pkm2)
    return floor(floor(((0.4 * pkm1.level + 2) * (atk / defe) * power) / 50 + 2)
                 * stab * effi * burn * item_mod * ability_mod * field_mod)


def effi_boost(move: dict, pkm1: Pokemon, pkm2: Pokemon) -> bool:
    """
    Calculate if boost is worth or not. Currently only working on speed.
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :return: Boolean, True if worth, else False
    """
    pkm1_spe = stat_calculation(pkm1.stats[Stats.SPE], pkm1.level, 252)
    move = next((i for i in pkm1.moves if i['name'] == move['move']))
    value = ((move.get('secondary') if move.get('secondary') else move)
        .get('self', move).get('boosts', {}).get('spe', 0))
    if not value:
        return False
    return (pkm2.compute_stat(Stats.SPE) > pkm1.compute_stat(Stats.SPE)
        and pkm1_spe * (value + pkm1.buff_affect(Stats.SPE)) > pkm2.compute_stat(Stats.SPE))


def effi_status(move: dict, pkm1: Pokemon, pkm2: Pokemon, team: Team) -> int:
    """
    Efficiency status calculator.
    Give arbitrary value to status move depending on types, abilities and stats.
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move
    :param pkm2: Pokemon that will receive move
    :param team: Team of pkm1
    :return: Integer, value of move [0, +oo[.
    """
    match move['status']:
        case 'tox' if "Poison" not in pkm2.types and "Steel" not in pkm2.types:
            return 100
        case 'par' if "Electric" not in pkm2.types or "Ground" not in pkm2.types:
            if pkm1.stats[Stats.SPE] - pkm2.stats[Stats.SPE] < 10:
                return 200
            return 100
        case 'brn' if "Fire" not in pkm2.types:
            if pkm2.stats[Stats.ATK] - pkm2.stats[Stats.SPA] > 10:
                return 200
            return 60
        case 'slp' if not ("Grass" in pkm2.types \
                or "Vital Spirit" in pkm2.abilities \
                or "Insomnia" in pkm2.abilities):
            for pkm in team.pokemons:  # Sleep clause
                if pkm.status == Status.SLP:
                    return 0
            return 200
    return 0


def effi_move(battle, move: dict, pkm1: Pokemon, pkm2: Pokemon, team: Team) -> int:
    """
    Calculate efficiency of move based on previous functions, type, base damage and item.
    :param battle: Battle instance
    :param move: Json object, status move.
    :param pkm1: Pokemon that will use move
    :param pkm2: Pokemon that will receive move
    :param team: Team of pkm1
    :return: Integer
    """
    if 'status' in move and pkm2.status == Status.UNK:
        return effi_status(move, pkm1, pkm2, team)
    return damage_calculation(battle, move, pkm1, pkm2)
