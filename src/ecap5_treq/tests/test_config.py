#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
# This file is part of ECAP5-TREQ <https://github.com/ECAP5/ECAP5-TREQ>
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

import os
from mock import patch, Mock, mock_open, call
import pytest

from ecap5_treq.config import Config, path_to_abs_path
from ecap5_treq.log import log_error, log_clear

#
# Fixture definitions
#

@pytest.fixture(autouse=True)
def reset():
    log_clear()

@pytest.fixture()
def stub_path_to_abs_path():
    def stubbed_path_to_abs_path(path, config_path = None):
        return path

    patcher = patch("ecap5_treq.config.path_to_abs_path", side_effect=stubbed_path_to_abs_path)
    stub = patcher.start()
    yield stub
    patcher.stop()

#
# Tests targetting Config class
#

def test_Config_constructor():
    """Unit test for the constructor of the Config class

    The covered behaviors are:
        * Constructor without a path
        * Constructor with a path
    """
    with patch.object(Config, "load_config") as stub_load_config:
        config = Config()
        stub_load_config.assert_not_called()

        config = Config("path")
        stub_load_config.assert_called_once_with("path")

def test_Config_load_config_01():
    """Unit test for the load_config method of the Config class

    The covered behavior is load_config with an empty configuration
    """
    empty_configuration = """{}"""
    with patch("builtins.open", mock_open(read_data=empty_configuration)):
        config = Config()
        config.load_config("path")
    assert len(config.data.keys()) == 0

def test_Config_load_config_02():
    """Unit test for the load_config method of the Config class

    The covered behavior is load_config with a configuration containing an unknown key
    """
    unknown_key_configuration = "{ \"spec_dir_path\": \"spec_dir_path\", \"unknown_key\": \"unknown_key\" }"
    with patch("builtins.open", mock_open(read_data=unknown_key_configuration)):
        config = Config()
        config.load_config("path")
        # An error log shall have been called
        assert len(log_error.msgs) == 1

def test_Config_load_config_03():
    """Unit test for the load_config method of the Config class

    The covered behavior is load_config with a configuration containing a syntax error
    """
    syntax_error_configuration = """{ \"spec_dir_path: \"spec_dir_path\" }"""
    with patch("builtins.open", mock_open(read_data=syntax_error_configuration)):
        config = Config()
        with pytest.raises(SystemExit) as e:
            config.load_config("path")
        # An error log shall have been called
        assert len(log_error.msgs) == 1

def test_Config_load_config_04(stub_path_to_abs_path):
    """Unit test for the load_config method of the Config class

    The covered behavior is load_config with a valid configuration
    """
    valid_configuration_with_path = "{ \"spec_dir_path\": \"spec_dir_path_content\", \"test_dir_path\": \"test_dir_path_content\" }"
    with patch("builtins.open", mock_open(read_data=valid_configuration_with_path)):
        config = Config()
        config.load_config("path")

    assert "spec_dir_path" in config.data
    assert "test_dir_path" in config.data
    # Check that the path_to_abs_path function has been called for the paths provided in the configuration
    stub_path_to_abs_path.assert_has_calls([call("spec_dir_path_content", "path"), call("test_dir_path_content", "path")])
    # The path_to_abs_path is stubbed to return the path untouched
    assert config.data["spec_dir_path"] == "spec_dir_path_content"
    assert config.data["test_dir_path"] == "test_dir_path_content"

def test_Config_get(stub_path_to_abs_path):
    """Unit test for the get method of the Config class

    The covered behavior are :
        * get an existing element
        * get a missing element
    """
    configuration = "{ \"spec_dir_path\": \"spec_dir_path_content\", \"test_dir_path\": \"test_dir_path_content\" }"
    with patch("builtins.open", mock_open(read_data=configuration)):
        config = Config()
        config.load_config("path")

    # Get elements
    assert config.get("spec_dir_path") == "spec_dir_path_content"
    assert config.get("test_dir_path") == "test_dir_path_content"

    # Get a missing element
    with pytest.raises(SystemExit) as e:
        config.get("unknown")
    # An error log shall have been called
    assert len(log_error.msgs) == 1

def test_Config_set():
    """Unit test for the set method of the Config class
    """
    config = Config()
    config.set("element1", "content1")
    config.set("element2", "content2")

    assert config.data["element1"] == "content1"
    assert config.data["element2"] == "content2"

def test_Config_set_path(stub_path_to_abs_path):
    """Unit test for the set_path method of the Config class
    """
    config = Config()
    config.set_path("element1", "content1")
    config.set_path("element2", "content2")

    assert config.data["element1"] == "content1"
    assert config.data["element2"] == "content2"

    stub_path_to_abs_path.assert_has_calls([call("content1"), call("content2")])

def test_Config___contains__():
    """Unit test for the __contains__ method of the Config class

    The covered behavior are :
        * check an existing element
        * check a missing element
    """
    config = Config()
    config.data["element1"] = "content1"
    config.data["element2"] = "content2"

    assert ("element1" in config) == True
    assert ("element2" in config) == True
    assert ("unknown" in config) == False

#
# Tests targetting functions in config module
#

def test_path_to_abs_path():
    """Unit test for the test_path_to_abs_path function

    The covered behavior are :
        * an empty path
        * a relative path from the current directory
        * a relative path from the configuration's directory
    """
    assert path_to_abs_path("") == ""
    # Relative path from the current directory
    assert path_to_abs_path("relative/path") == os.path.join(os.getcwd(), "relative/path")
    # Relative path from the config's directory
    assert path_to_abs_path("relative/path", "config/path") == os.path.join(os.path.abspath("config"), "relative/path")
    # Absolute path from the config's directory
    assert path_to_abs_path("/absolute/path") == "/absolute/path"
