import sys
import json

def load_config(path):
    data = None
    with open(path) as f:
        data = json.load(f)

    allowed_keys = [
        "spec_dir_path",
        "test_dir_path",
        "testdata_dir_path",
        "matrix_path"
    ]
    # check if there is any unknown key
    for key in data.keys():
        if key not in allowed_keys:
            print("ERROR: Unknown key \"{}\" while reading the {}".format(key, path), file=sys.stderr)

    return data

def check_config(config, mandatory_parameters):
    valid = True
    for p in mandatory_parameters:
        if p not in config:
            print("ERROR: {} is missing".format(p))
            valid = False
    if not valid:
        sys.exit(-1)
