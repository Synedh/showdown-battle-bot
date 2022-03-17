from src.pokemon import Stats, Pokemon, Team
from src.move_efficiency import effi_move, effi_boost, base_damages


def effi_pkm(battle, pkm1: Pokemon, pkm2: Pokemon, team1: Team, team2: Team) -> int:
    """
    Efficiency of pokemon against other.
    Based on move efficiency functions.
    If efficiency of a pokemon > 150 and is faster, efficiency of the other pokemon is not taken.
    effi_pkm(a, b, team_a) = - effi_pkm(b, a, team_b)
    :param battle: Battle object, current battle.
    :param pkm1: Pokemon that will use move.
    :param pkm2: Pokemon that will receive move.
    :param team1: Team of pkm1.
    :param team2: Team of pkm2.
    :return: Integer, can be negative.
    """
    pkm1_spe = pkm1.compute_stat(Stats.SPE)
    pkm2_spe = pkm2.compute_stat(Stats.SPE)

    effi1 = max([effi_move(battle, move, pkm1, pkm2, team2) for move in pkm1.moves])
    if effi1 >= base_damages(150, pkm1, pkm2) and pkm1_spe > pkm2_spe:
        return effi1
    effi2 = max([effi_move(battle, move, pkm2, pkm1, team1) for move in pkm2.moves])
    if effi2 >= base_damages(150, pkm2, pkm1) and pkm2_spe > pkm1_spe:
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
                pkm_efficiency = effi_pkm(battle, pokemon, enemy_pkm, team, enemy_team)
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
        if effi_pkm(battle, pokemon, enemy_pkm, team, battle.enemy_team) > effi:
            best_pkm = pokemon
            effi = effi_pkm(battle, pokemon, enemy_pkm, team, battle.enemy_team)
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
    best_move = -1, -1024

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
    bot_pkm = battle.bot_team.active()
    enm_pkm = battle.enemy_team.active()
    move_id, best_bot_atk = make_best_move(battle)
    best_enm_atk = max(
        effi_move(battle, move, enm_pkm, bot_pkm, battle.bot_team)
        for move in enm_pkm.moves
    )

    switch_id, switch_value = make_best_switch(battle)
    effi_bot_pkm = effi_pkm(battle, bot_pkm, enm_pkm, battle.bot_team, battle.enemy_team)

    print(f'{best_bot_atk=}, {best_enm_atk=}, {switch_value=}, {effi_bot_pkm=}')

    if (switch_id > 0 and switch_value > effi_bot_pkm
        and (best_enm_atk > base_damages(150, bot_pkm, enm_pkm)
             and bot_pkm.compute_stat(Stats.SPE) < enm_pkm.compute_stat(Stats.SPE)
             or best_bot_atk < base_damages(100, bot_pkm, enm_pkm))):
        return 'switch', switch_id
    return 'move', move_id
