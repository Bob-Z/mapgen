import json
import sys

with open("config.json", "r") as file:
    data = json.load(file)

for arg in sys.argv[1:]:
    if '=' not in arg:
        print("Invalid parameter '" + arg + "', expected key=value")
        sys.exit(1)
    param_name, param_value = arg.split('=', 1)
    if param_name not in data:
        print("Unknown parameter:", param_name)
        sys.exit(1)
    print("Parameter", param_name, "set to", param_value)
    try:
        if type(data[param_name]) is bool:
            if param_value.lower() in ['true', '1', 't', 'y', 'yes']:
                param_value = True
            else:
                param_value = False
        elif type(data[param_name]) is float:
            param_value = float(param_value)
        elif type(data[param_name]) is int:
            param_value = int(param_value)
    except ValueError:
        print("Invalid value for", param_name + ":", param_value)
        sys.exit(1)
    data[param_name] = param_value
