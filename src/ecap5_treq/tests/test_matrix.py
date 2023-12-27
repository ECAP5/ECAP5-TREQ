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

import os
from mock import patch, Mock, mock_open, call
import pytest

from ecap5_treq.matrix import Matrix, prepare_matrix
from ecap5_treq.check import Check
from ecap5_treq.log import log_error, log_clear

#
# Fixture definitions
#

@pytest.fixture(autouse=True)
def reset():
    log_clear()

#
# Tests targetting Matrix class
#

def test_Matrix_constructor():
    """Unit test for the constructor of the Matrix class

    The covered behaviors are:
        * Constructor without a path
        * Constructor with a path
    """
    with patch.object(Matrix, "read") as stub_read:
        matrix = Matrix()
        stub_read.assert_not_called()

        matrix = Matrix("path")
        stub_read.assert_called_once_with("path")

def test_Matrix_read_01():
    """Unit test for the read method of the Matrix class

    The covered behavior is an empty matrix
    """
    empty_matrix = ""
    with patch("builtins.open", mock_open(read_data=empty_matrix)):
        matrix = Matrix()
        matrix.read("path")

    assert len(matrix.data.keys()) == 0

def test_Matrix_read_02():
    """Unit test for the read method of the Matrix class

    The covered behavior is an valid matrix
    """
    valid_matrix = "element1;content1\nelement2;content2;content3"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        matrix = Matrix()
        matrix.read("path")

    assert len(matrix.data.keys()) == 2
    assert "element1" in matrix.data
    assert "element2" in matrix.data
    assert matrix.data["element1"] == ["content1"]
    assert matrix.data["element2"] == ["content2", "content3"]

def test_Matrix_read_03():
    """Unit test for the read method of the Matrix class

    The covered behavior is an valid matrix containing an empty element
    """
    empty_element_matrix = "element1;content1\nelement2"
    with patch("builtins.open", mock_open(read_data=empty_element_matrix)):
        matrix = Matrix()
        matrix.read("path")

    assert len(matrix.data.keys()) == 2
    assert "element1" in matrix.data
    assert "element2" in matrix.data
    assert matrix.data["element1"] == ["content1"]
    assert matrix.data["element2"] == []

def test_Matrix_check_01():
    """Unit test for the check method of the Matrix class

    The covered behavior is a check equal to true
    """
    valid_matrix = "element2;content1\nelement1;content2;content3\n__UNTRACEABLE__\n"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        matrix = Matrix()
        matrix.read("path")

    checks = [Check(None, "element1"), Check(None, "element2")]
    assert matrix.check(checks) == True

def test_Matrix_check_02():
    """Unit test for the check method of the Matrix class

    The covered behavior is a check equal to false due to the list of checks missing an element
    """
    valid_matrix = "element1;content1\nelement2;content2;content3\n__UNTRACEABLE__\n"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        matrix = Matrix()
        matrix.read("path")

    checks = [Check(None, "element1")]
    assert matrix.check(checks) == False

def test_Matrix_check_03():
    """Unit test for the check method of the Matrix class

    The covered behavior is a check equal to false due to the matrix missing the __UNTRACEABLE__ entry
    """
    valid_matrix = "element1;content1\nelement2;content2;content3"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        matrix = Matrix()
        matrix.read("path")

    checks = [Check(None, "element1"), Check(None, "element2")]
    assert matrix.check(checks) == False

def test_Matrix_add():
    """Unit test for the add method of the Matrix class
    """
    valid_matrix = "element1;content1\nelement2;content2;content3"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        matrix = Matrix()
        matrix.read("path")

    # Check that the element was not present before
    assert "added_element" not in matrix.data

    # Add the element
    matrix.add("added_element", ["content1", "content2"])

    # Check that the element was properly added
    assert "added_element" in matrix.data
    assert matrix.data["added_element"] == ["content1", "content2"]

def test_Matrix_get():
    """Unit test for the get method of the Matrix class

    The covered behaviors are:
        * get with an existing element
        * get with a missing element
    """
    valid_matrix = "element1;content1\nelement2;content2;content3"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        matrix = Matrix()
        matrix.read("path")

    assert matrix.get("element1") == ["content1"]
    assert matrix.get("unknown") == []
    
def test_Matrix___contains__():
    """Unit test for the __contains__ method of the Matrix class

    The covered behaviors are:
        * check with an existing element
        * check with a missing element
    """
    valid_matrix = "element1;content1\nelement2;content2;content3"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        matrix = Matrix()
        matrix.read("path")

    assert "element1" in matrix.data
    assert "unknown" not in matrix.data

def test_Matrix___eq__():
    """Unit test for the __eq__ method of the Matrix class
    """
    matrix = Matrix()
    matrix.add("key1", "content1")
    matrix.add("key2", "content2")
    matrix.add("key3", "content3")

    other = Matrix()
    other.add("key1", "content1")
    other.add("key2", "content2")
    other.add("key3", "content3")

    assert matrix == other

    other.add("key4", "content4")
    assert matrix != other

def test_Matrix_to_csv():
    """Unit test for the to_csv method of the Matrix class
    """
    valid_matrix = "element1;content1\nelement2;content2;content3\n__UNTRACEABLE__"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        base_matrix = Matrix()
        base_matrix.read("path")
    base_matrix_csv_str = base_matrix.to_csv()

    # Generate a matrix from the string
    with patch("builtins.open", mock_open(read_data=base_matrix_csv_str)):
        new_matrix = Matrix()
        new_matrix.read("path")

    # Compare the two matrices
    assert base_matrix.data == new_matrix.data

def test_Matrix___repr__():
    """Unit test for the __repr__ method of the Matrix class
    """
    valid_matrix = "element1;content1\nelement2;content2;content3\n__UNTRACEABLE__"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        base_matrix = Matrix()
        base_matrix.read("path")
    base_matrix_csv_str = repr(base_matrix)

    # Generate a matrix from the string
    with patch("builtins.open", mock_open(read_data=base_matrix_csv_str)):
        new_matrix = Matrix()
        new_matrix.read("path")

    # Compare the two matrices
    assert base_matrix.data == new_matrix.data

def test_Matrix___str__():
    """Unit test for the __str__ method of the Matrix class
    """
    valid_matrix = "element1;content1\nelement2;content2;content3\n__UNTRACEABLE__"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        base_matrix = Matrix()
        base_matrix.read("path")
    base_matrix_csv_str = str(base_matrix)

    # Generate a matrix from the string
    with patch("builtins.open", mock_open(read_data=base_matrix_csv_str)):
        new_matrix = Matrix()
        new_matrix.read("path")

    # Compare the two matrices
    assert base_matrix.data == new_matrix.data

#
# Tests targetting functions in matrix module
#

def test_prepare_matrix_01():
    """Unit test for the prepare_matrix function

    The covered behavior is with the previous matrix being None
    """
    checks = [Check(None, "check1"), Check(None, "check2")]
    matrix = prepare_matrix(checks, None)

    assert len(matrix.data) == 3
    assert "check1" in matrix.data
    assert "check2" in matrix.data
    assert "__UNTRACEABLE__" in matrix.data
    assert matrix.data["check1"] == []
    assert matrix.data["check2"] == []
    assert matrix.data["__UNTRACEABLE__"] == []

def test_prepare_matrix_02():
    """Unit test for the prepare_matrix function

    The covered behavior is with an empty previous matrix
    """
    checks = [Check(None, "check1"), Check(None, "check2")]
    previous_matrix = Matrix()
    matrix = prepare_matrix(checks, previous_matrix)

    assert len(matrix.data) == 3
    assert "check1" in matrix.data
    assert "check2" in matrix.data
    assert "__UNTRACEABLE__" in matrix.data
    assert matrix.data["check1"] == []
    assert matrix.data["check2"] == []
    assert matrix.data["__UNTRACEABLE__"] == []

def test_prepare_matrix_03():
    """Unit test for the prepare_matrix function

    The covered behavior is with a previous matrix containing one of the check and having an untraceable element
    """
    checks = [Check(None, "check1"), Check(None, "check2")]
    valid_matrix = "element1;content1\ncheck2;content2;content3\n__UNTRACEABLE__;content4"
    with patch("builtins.open", mock_open(read_data=valid_matrix)):
        previous_matrix = Matrix()
        previous_matrix.read("path")
    matrix = prepare_matrix(checks, previous_matrix)

    assert len(matrix.data) == 3
    assert "check1" in matrix.data
    assert "check2" in matrix.data
    assert "__UNTRACEABLE__" in matrix.data
    assert matrix.data["check1"] == []
    assert matrix.data["check2"] == ["content2", "content3"]
    assert matrix.data["__UNTRACEABLE__"] == ["content4"]
