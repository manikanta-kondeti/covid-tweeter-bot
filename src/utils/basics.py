import json


def read_variable_from_file(variable_name):
    data = open("tokens.json")
    json_decoded = json.load(data)
    return json_decoded[variable_name] or None