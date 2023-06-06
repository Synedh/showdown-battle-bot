import re
from src.battle import Battle


def major_actions(battle: Battle, command: str, split_line: list[str]):
    match command:
        case "move":
            pass
        case "switch" if battle.player_id not in split_line[0]:
            # Enemy pokemon has switched in
            print('|'.join(split_line[0:2]))
            regex = re.compile(r'p\da: (.*?)\|(.*?), (?:L(\d+), )?.*')
            name, variant, level = regex.match('|'.join(split_line[0:2])).groups()
            battle.update_enemy(name, split_line[2], variant, level if level else '100')
        case "swap":
            pass
        case "detailschange":
            pass
        case "cant":
            pass
        case "faint":
            pass
        case _:
            pass


def minor_actions(battle: Battle, command: str, split_line: list[str]):
    match command:
        case "-fail":
            pass
        case "-damage" if battle.player_id not in split_line[0]:
            name = re.match(r'p\da: (.*)', split_line[0]).group(1)
            battle.update_enemy(name, split_line[1])
        case "-heal":
            pass
        case "-status":
            battle.update_status(battle.get_team(split_line[0]).active(), split_line[1])
        case "-curestatus":
            battle.update_status(battle.get_team(split_line[0]).active())
        case "-cureteam":
            pass
        case "-boost":
            battle.set_buff(battle.get_team(split_line[0]).active(), split_line[1], int(split_line[2]))
        case "-unboost":
            battle.set_buff(battle.get_team(split_line[0]).active(), split_line[1], - int(split_line[2]))
        case "-weather":
            battle.weather = split_line[0]
        case "-fieldstart":
            battle.fields.append(split_line[0])
        case "-fieldend":
            battle.fields.remove(split_line[0])
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
            battle.get_team(split_line[0]).active().item = split_line[1].lower().replace(" ", "")
        case "-enditem":
            battle.get_team(split_line[0]).active().item = None
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


def battlelog_parsing(battle: Battle, command: str, split_line: list[str]):
    if command.startswith('-'):
        minor_actions(battle, command, split_line)
    else:
        major_actions(battle, command, split_line)
