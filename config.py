import json

data = {}

with open("config.json", "r") as file:
    data = json.load(file)
