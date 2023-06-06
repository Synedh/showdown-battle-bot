from src.pokemon import Stats, Pokemon, Team
from src.move_efficiency import effi_move, effi_boost, comparator_calculation


def effi_pkm(battle, pkm1: Pokemon, pkm2: Pokemon, team: Team) -> int:
    """
    Efficiency of pokemon against other.
    Based on move efficiency functions.
    If efficiency of a pokemon > 150 and is faster, efficiency of the other pokemon is not taken.
    effi_pkm(a, b, team_a) = - effi_pkm(b, a, team_b)
    :param battle: Battle object, current battle.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :param team: Team of pkm1.
    :return: Integer, can be negative.
    """
    pkm1_spe = pkm1.compute_stat(Stats.SPE)
    pkm2_spe = pkm2.compute_stat(Stats.SPE)

    effi1 = max([effi_move(battle, move, pkm1, pkm2, team) for move in pkm1.moves])
    if effi1 >= comparator_calculation(150, pkm1, pkm2) and pkm1_spe > pkm2_spe:
        return effi1
    effi2 = max([effi_move(battle, move, pkm2, pkm1, team) for move in pkm2.moves])
    if effi2 >= comparator_calculation(150, pkm1, pkm2) and pkm2_spe > pkm1_spe:
        return -effi2
    return effi1 - effi2


def make_best_order(battle, form: str = None) -> list[Pokemon]:
    """
    Parse battle.bot_team to find the best pokemon based on his damages against enemy team.
    :param battle: Battle object, current battle.
    :param form: Battle format.
    :return: List of pokemons in bot_team sorted by efficiency ([[1, 6], [-oo, +oo]]).
    """
    team = battle.bot_team
    enemy_team = battle.enemy_team
    ordered_team = []
    for i, pokemon in enumerate(team.pokemons):
        average_efficiency = 0
        for enemy_pkm in enemy_team.pokemons:
            pkm_efficiency = -1024
            if form == 'gen8challengecup1v1':
                for move in pokemon.moves:
                    dmg = effi_move(battle, move, pokemon, enemy_pkm, team)
                    if pkm_efficiency < dmg:
                        pkm_efficiency = dmg
            elif form in ["gen6battlefactory", "gen8bssfactory"]:
                pkm_efficiency = effi_pkm(battle, pokemon, enemy_pkm, enemy_team)
            average_efficiency += pkm_efficiency
        average_efficiency /= 6
        ordered_team.append([i + 1, average_efficiency])
        ordered_team.sort(key=lambda x: x[1], reverse=True)
    return ordered_team


def make_best_switch(battle) -> tuple[int, int]:
    """
    Parse battle.bot_team to find the best pokemon based on his efficiency against current enemy pokemon.
    :param battle: Battle object, current battle.
    :return: (Index of pokemon in bot_team (Integer, [-1, 6]), efficiency (Integer, [0, +oo[))
    """
    team = battle.bot_team
    enemy_pkm = battle.enemy_team.active()
    best_pkm = None
    effi = -1024
    for pokemon in team.pokemons:
        if pokemon == team.active() or pokemon.condition == "0 fnt":
            continue
        if effi_pkm(battle, pokemon, enemy_pkm, battle.enemy_team) > effi:
            best_pkm = pokemon
            effi = effi_pkm(battle, pokemon, enemy_pkm, battle.enemy_team)
    try:
        return team.pokemons.index(best_pkm) + 1, effi
    except ValueError:
        return -1, -1024


def make_best_move(battle) -> tuple[int,int]:
    """
    Parse attacks of current pokemon and send the most efficient based on previous function
    :param battle: Battle object, current battle.
    :return: (Index of move in pokemon (Integer, [-1, 4]), efficiency (Integer, [0, +oo[))
    """
    pokemon_moves = battle.current_pkm[0]['moves']
    pokemon = battle.bot_team.active()
    enemy_pkm = battle.enemy_team.active()
    best_move = 1, 0

    for i, move in enumerate(pokemon_moves):
        if move.get('disabled'):
            continue
        full_move = next(m for m in pokemon.moves if m['name'] == move['move'])
        effi = effi_move(battle, full_move, pokemon, enemy_pkm, battle.enemy_team)
        if effi > best_move[1]:
            best_move = (i + 1, effi)
        print(move['move'], effi)

    for i, move in enumerate(pokemon_moves):  # Boosts handling
        if effi_boost(move, pokemon, enemy_pkm):
            best_move = (i + 1, best_move[1] + 1)
    print('Best', pokemon_moves[best_move[0] - 1]['move'], best_move[1])
    return best_move


def make_best_action(battle) -> tuple[str, int]:
    """
    Global function to choose best action to do each turn.
    Select best action of bot and enemy pokemon, then best pokemon to switch. And finally, chose if it worth or not to
    switch.
    :param battle: Battle object, current battle.
    :return: (Index of move in pokemon (["move"|"switch"], [-1, 6]))
    """
    best_enm_atk = 0
    best_bot_atk = 0
    bot_pkm = battle.bot_team.active()
    enm_pkm = battle.enemy_team.active()
    for move in bot_pkm.moves:
        effi = effi_move(battle, move, bot_pkm, enm_pkm, battle.enemy_team)
        if best_bot_atk < effi:
            best_bot_atk = effi
    for move in enm_pkm.moves:
        effi = effi_move(battle, move, enm_pkm, bot_pkm, battle.enemy_team)
        if best_enm_atk < effi:
            best_enm_atk = effi

    switch_id, switch_value = make_best_switch(battle)
    if (switch_value > effi_pkm(battle, bot_pkm, enm_pkm, battle.enemy_team)
        and (best_enm_atk > comparator_calculation(150, bot_pkm, enm_pkm)
             and (bot_pkm.stats[Stats.SPE] * bot_pkm.buff_affect(Stats.SPE)
                  - enm_pkm.stats[Stats.SPE] * bot_pkm.buff_affect(Stats.SPE)) < 10
             or best_bot_atk < comparator_calculation(100, bot_pkm, enm_pkm)) and switch_id):
        return 'switch', switch_id
    return 'move', make_best_move(battle)[0]
