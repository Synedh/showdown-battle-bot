from src.battle import Battle


# def pkm_data(battle: Battle, pokemon_str):
#     if battle.player_id in pokemon_str.split(':')[0]:
#         return battle.bot_team.active()
#     else:
#         return battle.enemy_team.active()


def major_actions(battle: Battle, split_line):
    if split_line[0] == "move":
        pass
    elif split_line[0] == "switch":
        if battle.player_id not in split_line[1]:
            battle.update_enemy(split_line[2].split(',')[0], split_line[2].split(',')[1].split('L')[1], split_line[3])
    elif split_line[0] == "swap":
        pass
    elif split_line[0] == "detailschange":
        pass
    elif split_line[0] == "cant":
        pass
    elif split_line[0] == "faint":
        pass
    else:
        pass


def minor_actions(battle: Battle, split_line):
    if split_line[0] == "-fail":
        pass
    elif split_line[0] == "-damage":
        pass
    elif split_line[0] == "-heal":
        pass
    elif split_line[0] == "-status":
        if battle.player_id in split_line[1]:
            battle.update_status(battle.bot_team.active(), split_line[2])
        else:
            battle.update_status(battle.enemy_team.active(), split_line[2])
    elif split_line[0] == "-curestatus":
        if battle.player_id in split_line[1]:
            battle.update_status(battle.bot_team.active())
        else:
            battle.update_status(battle.enemy_team.active())
    elif split_line[0] == "-cureteam":
        pass
    elif split_line[0] == "-boost":
        if battle.player_id in split_line[1]:
            battle.set_buff(battle.bot_team.active(), split_line[2], int(split_line[3]))
        else:
            battle.set_buff(battle.enemy_team.active(), split_line[2], int(split_line[3]))
    elif split_line[0] == "-unboost":
        if battle.player_id in split_line[1]:
            battle.set_buff(battle.bot_team.active(), split_line[2], - int(split_line[3]))
        else:
            battle.set_buff(battle.enemy_team.active(), split_line[2], - int(split_line[3]))
    elif split_line[0] == "-weather":
        pass
    elif split_line[0] == "-fieldstart":
        pass
    elif split_line[0] == "-fieldend":
        pass
    elif split_line[0] == "-sidestart":
        pass
    elif split_line[0] == "-sideend":
        pass
    elif split_line[0] == "-crit":
        pass
    elif split_line[0] == "-supereffective":
        pass
    elif split_line[0] == "-resisted":
        pass
    elif split_line[0] == "-immune":
        pass
    elif split_line[0] == "-item":
        if battle.player_id not in split_line[1]:
            battle.set_enemy_item(split_line[2])
    elif split_line[0] == "-enditem":
        if battle.player_id not in split_line[1]:
            battle.set_enemy_item("")
    elif split_line[0] == "-ability":
        pass
    elif split_line[0] == "-endability":
        pass
    elif split_line[0] == "-transform":
        pass
    elif split_line[0] == "-mega":
        pass
    elif split_line[0] == "-activate":
        pass
    elif split_line[0] == "-hint":
        pass
    elif split_line[0] == "-center":
        pass
    elif split_line[0] == "-message":
        pass
    else:
        pass


def battlelog_parsing(battle: Battle, split_line):
    if split_line[0][0] != "-":
        major_actions(battle, split_line)
    else:
        minor_actions(battle, split_line)
