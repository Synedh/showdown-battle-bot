import json


def efficiency(elem, elem1, elem2=None):
    res = 1
    with open('data/typechart.json') as data_file:
        typechart = json.load(data_file)
    tmp = typechart[elem1]['damageTaken'][elem]
    if tmp == 1:
        res *= 2
    elif tmp == 2:
        res *= 0.5
    elif tmp == 3:
        res *= 0
    if elem2:
        tmp = typechart[elem2]['damageTaken'][elem]
        if tmp == 1:
            res *= 2
        elif tmp == 2:
            res *= 0.5
        elif tmp == 3:
            res *= 0
    return res
