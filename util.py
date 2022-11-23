import json
from typing import Dict


def read_file(path: str):
    with open(path, 'r') as file:
        data = file.read()
        return json.loads(data)


def values_to_keys(d: Dict):
    new_dic = {}
    for k, v in d.items():
        new_dic[v] = new_dic.get(v, []) + [k]
    return new_dic
