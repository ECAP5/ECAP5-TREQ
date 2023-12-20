import sys
import json
import os
from log import *

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
            log_error("Unknown key \"{}\" while reading config at {}".format(key, path))

    return data

def check_config(config, mandatory_parameters):
    valid = True
    for p in mandatory_parameters:
        if p not in config:
            log_error("The \"{}\" config parameter is missing".format(p))
            valid = False
    if not valid:
        sys.exit(-1)
