#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
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

# pylint: disable=missing-function-docstring

import os

from ecap5_treq.config import path_to_abs_path

def test_Config_load_config():
    config = Config()

def test_path_to_abs_path():
    assert path_to_abs_path("") == ""
    # Relative path from the current directory
    assert path_to_abs_path("relative/path") == os.path.join(os.getcwd(), "relative/path")
    # Relative path from the config's directory
    assert path_to_abs_path("relative/path", "config/path") == os.path.join(os.path.abspath("config"), "relative/path")
