from src.battle import Battle
from src.move_efficiency import *
from src.pokemon import Pokemon, Team


def effi_pkm(pkm1: Pokemon, pkm2: Pokemon, team: Team) -> int:
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


def make_best_switch(battle: Battle) -> (int, int):
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


def make_best_move(battle: Battle) -> (int, int):
    """
    Parse attacks of current pokemon and send the most efficient based on previous function
    :param battle: Battle object, current battle.
    :return: (Index of move in pokemon (Integer, [-1, 4]), efficiency (Integer, [0, +oo]))
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


def make_best_action(battle: Battle) -> (str, int):
    """
    Global function to choose best action to do each turn.
    Select best action of bot and enemy pokemon, then best pokemon to switch. And finally, chose if it worth or not to
    switch.
    :param battle: Battle object, current battle.
    :return: (["move"|"switch"], [-1, 6])
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
