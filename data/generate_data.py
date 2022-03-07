import re
import requests

BASE_URL = 'https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/'


def parse_value(value):
    if value[0] == '[':
        return [parse_value(val) for val in re.split(r',\s*', value[1:-1])]
    if value[0] == '{':
        parsed_value = {}
        for str_data in re.split(r',\s*', value[1:-1]):
            key, val = re.split(r':\s*', str_data)
            parsed_value[key] = parse_value(val)
        return parsed_value
    if value[0] == '"':
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def get_pokemon_info(data, line):
    line += 1
    if groups := re.match(r'\s*(\w+): (.+),', data[line]):
        next_line, line = get_pokemon_info(data, line)
        return {groups.group(1): parse_value(groups.group(2)), **next_line}, line
    return {}, line

def get_key_value(data):
    i = 0
    pokedex = {}
    line_match = lambda regex: re.fullmatch(regex, data[i])
    while not line_match(r'};'):
        if groups := line_match(r'\s*(\w+): {'):
            value, i = get_pokemon_info(data, i)
            pokedex[groups.group(1)] = value
        i += 1
    return pokedex
    
endpoints = ['pokedex.ts', 'formats-data.ts', 'moves.ts', 'typechart.ts']
data = requests.get(f'{BASE_URL}{endpoints[2]}').text.splitlines()
print(get_key_value(data).items()[0])
