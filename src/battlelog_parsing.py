from src.battle import Battle


def major_actions(battle: Battle, command: str, split_line):
    match command:
        case "move":
            pass
        case "switch":
            if battle.player_id not in split_line[0]:
                battle.update_enemy(split_line[1].split(',')[0], split_line[1].split(',')[1].split('L')[1], split_line[2])
        case "swap":
            pass
        case "detailschange":
            pass
        case "cant":
            pass
        case "faint":
            pass
        case "poke":
            if battle.player_id not in split_line[0]:
                pkm = split_line[1].split(', ')
                battle.update_enemy(pkm[0], pkm[1][1:] if len(pkm) > 1 and 'L' in pkm[1] else '100', 100)
        case _:
            pass


def minor_actions(battle: Battle, command: str, split_line):
    match command:
        case "-fail":
            pass
        case "-damage":
            pass
        case "-heal":
            pass
        case "-status":
            if battle.player_id in split_line[0]:
                battle.update_status(battle.bot_team.active(), split_line[1])
            else:
                battle.update_status(battle.enemy_team.active(), split_line[1])
        case "-curestatus":
            if battle.player_id in split_line[0]:
                battle.update_status(battle.bot_team.active())
            else:
                battle.update_status(battle.enemy_team.active())
        case "-cureteam":
            pass
        case "-boost":
            if battle.player_id in split_line[0]:
                battle.set_buff(battle.bot_team.active(), split_line[1], int(split_line[2]))
            else:
                battle.set_buff(battle.enemy_team.active(), split_line[1], int(split_line[2]))
        case "-unboost":
            if battle.player_id in split_line[0]:
                battle.set_buff(battle.bot_team.active(), split_line[1], - int(split_line[2]))
            else:
                battle.set_buff(battle.enemy_team.active(), split_line[1], - int(split_line[2]))
        case "-weather":
            pass
        case "-fieldstart":
            pass
        case "-fieldend":
            pass
        case "-sidestart":
            if "Reflect" in split_line[1] or "Light Screen" in split_line[1]:
                battle.screens[split_line[1].split(":")[1].lower().replace(" ", "")] = True
                print("** " + battle.screens)
        case "-sideend":
            if "Reflect" in split_line[1] or "Light Screen" in split_line[1]:
                battle.screens[split_line[1].split(":")[1].lower().replace(" ", "")] = False
                print("** " + battle.screens)
        case "-crit":
            pass
        case "-supereffective":
            pass
        case "-resisted":
            pass
        case "-immune":
            pass
        case "-item":
            if battle.player_id in split_line[0]:
                battle.bot_team.active().item = split_line[1].lower().replace(" ", "")
            else:
                battle.enemy_team.active().item = split_line[1].lower().replace(" ", "")
        case "-enditem":
            if battle.player_id not in split_line[0]:
                battle.bot_team.active().item = None
            else:
                battle.enemy_team.active().item = None
        case "-ability":
            pass
        case "-endability":
            pass
        case "-transform":
            pass
        case "-mega":
            pass
        case "-activate":
            pass
        case "-hint":
            pass
        case "-center":
            pass
        case "-message":
            pass
        case _:
            pass


def battlelog_parsing(battle: Battle, command: str, split_line):
    if command.startswith('-'):
        minor_actions(battle, command, split_line)
    else:
        major_actions(battle, command, split_line)
