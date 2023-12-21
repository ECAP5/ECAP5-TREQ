#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaie
# This file is part of ECAP5-TREQ <https://github.com/cchaine/ECAP5-TREQ>
# 
# ECAP5-TREQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ECAP5-TREQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ECAP5-TREQ.  If not, see <http://www.gnu.org/licenses/>.

import sys
import json
import os

from ecap5_treq.log import *

class Config:
    """A Config stores input parameters such as paths to the specification, 
    tests, testdata or the traceability matrix.
    """

    def __init__(self, path: str = None):
        """Contructor of Config
        
        :param path: path to the configuration file. The Config object will be empty if no path is provided
        :type path: str
        """
        self.data = {}
        self.path = path

        if self.path:
            self.load_config(path)

    def load_config(self, path: str) -> None:
        """Loads the Config object with data from the configuration file pointed by path.
        
        :param path: path to the configuration file.
        :type path: str
        """
        self.path = path

        # Load a dictionary from the json configuration file
        self.data = None
        with open(path) as f:
            self.data = json.load(f)

        allowed_path_keys = [
            "spec_dir_path",
            "test_dir_path",
            "testdata_dir_path",
            "matrix_path"
        ]
        allowed_other_keys = []

        # Check if there are any unknown keys
        for key in self.data.keys():
            if key not in allowed_path_keys + allowed_other_keys:
                log_error("Unknown key \"{}\" while reading config at {}".format(key, path))
            else:
                # If the key is a path, convert the path to an absolute path
                if key in allowed_path_keys:
                    self.data[key] = path_to_abs_path(self.data[key], self.path)

    def get(self, key: str) -> str:
        """Return the configuration data pointed by key
        
        :param key: key used to identify the configuration data
        :type key: str

        :returns: the configuration data pointed by key
        :rtype: str
        """
        if key not in self.data:
            log_error("The \"{}\" config parameter is missing".format(key))
            # The program is interrupted here as this is a critical error
            sys.exit(-1)
        else:
            return self.data[key]

    def set(self, key: str, value: str) -> None:
        """Set the value of the configuration data pointed by key to the provided value.
        
        :param key: key used to identify the configuration data
        :type key: str

        :param value: value to be written
        :type value: str
        """
        self.data[key] = value

    def set_path(self, key: str, path: str) -> None:
        """Set the path value of the configuration data pointed by key to the provided value.

        This function is used instead of set() when dealing with paths as this function converts
        paths to absolute paths.
        
        :param key: key used to identify the configuration data
        :type key: str

        :param path: path to be written
        :type path: str
        """
        # Convert the path to absolute path
        abs_path = path_to_abs_path(path)

        self.data[key] = abs_path

    def __contains__(self, key: str) -> bool:
        """Override of the __contains__ function used to check if a key belongs to the configuration data
        
        :param key: key used to identify the configuration data
        :type key: str

        :returns: a boolean indicating if key belongs to the configuration data
        :rtype: bool
        """
        return key in self.data

def path_to_abs_path(path: str, config_path: str = None) -> str:
    """Converts a path to absolute

    :param path: the path to convert to absolute path
    :type path: str

    :param config_path: path to the configuration file if provided, None otherwise
    :type config_path: str

    :return: The relative path from either the config directory or current directory to the file pointed by path
    :rtype: str
    """
    if len(path) > 0:
        # If the path is relative
        if path[0] != "/":
            parent_dir = None
            if config_path != None:
                # Get the directory of the configuration file
                parent_dir = os.path.dirname(config_path)
            else:
                parent_dir = os.getcwd()
            path = os.path.join(os.path.abspath(parent_dir), path)
    return path
