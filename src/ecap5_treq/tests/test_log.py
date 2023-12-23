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

import pytest

from ecap5_treq.log import log_imp, log_warn, log_error, log_clear

#
# Fixture definitions
#

@pytest.fixture(autouse=True)
def reset():
    log_clear()

#
# Tests targetting functions in log module
#

def test_log_imp():
    """Unit test for log_imp
    """
    # The log shall be empty at startup 
    assert len(log_imp.msgs) == 0

    for i in range(10):
        log_imp("{}".format(i))

    # Check the number of logged messages
    assert len(log_imp.msgs) == 10
    # Check the logged messages
    for i in range(10):
        assert log_imp.msgs[i] == "{}".format(i)

def test_log_warn():
    """Unit test for log_imp
    """
    # The log shall be empty at startup 
    assert len(log_warn.msgs) == 0

    for i in range(10):
        log_warn("{}".format(i))

    # Check the number of logged messages
    assert len(log_warn.msgs) == 10
    # Check the logged messages
    for i in range(10):
        assert log_warn.msgs[i] == "{}".format(i)

def test_log_error():
    """Unit test for log_imp
    """
    # The log shall be empty at startup 
    assert len(log_error.msgs) == 0

    for i in range(10):
        log_error("{}".format(i))

    # Check the number of logged messages
    assert len(log_error.msgs) == 10
    # Check the logged messages
    for i in range(10):
        assert log_error.msgs[i] == "{}".format(i)
