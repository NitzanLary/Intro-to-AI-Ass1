import json


def read_file(path: str):
    with open(path, 'r') as file:
        data = file.read()
        return json.loads(data)
