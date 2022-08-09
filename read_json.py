import json


def read_json_file(filepath: str) -> dict:
    with open(filepath, "r") as json_file:
        return json.load(json_file)


def write_json_file(data: dict, filepath: str):
    with open(filepath, "w") as json_file:
        json_file.write(json.dumps(data, indent=2))
