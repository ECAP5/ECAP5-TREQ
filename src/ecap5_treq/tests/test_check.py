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
import contextlib
from mock import patch, Mock, mock_open, call
import pytest
import io

from ecap5_treq.check import Check, import_checks, import_testdata
from ecap5_treq.log import log_error, log_warn, log_clear

#
# Fixture definitions
#

@pytest.fixture(autouse=True)
def reset():
    log_clear()
    stubbed_glob.file_list = []
    stubbed_open.file_contents = {}

def stubbed_glob(path, recursive=True):
    return stubbed_glob.file_list

def stubbed_open(path, encoding = "", newline=""):
    reader = io.BufferedReader(io.BytesIO(stubbed_open.file_contents[path].encode(encoding)))
    output = io.TextIOWrapper(reader)
    return output

#
# Tests targetting Check class
#

def test_Check_constructor():
    """Unit test for the constructor of the Check class

    The covered behaviors are:
        * Constructor without testsuite
        * Constructor with testsuite
        * Constructor without status
        * Constructor with status
    """
    check = Check(None, "check1")
    assert check.testsuite == None
    assert check.id == "check1"
    assert check.status == None
    assert check.error_msg == None

    check = Check("testsuite", "check1")
    assert check.testsuite == "testsuite"
    assert check.id == "testsuite.check1"
    assert check.status == None
    assert check.error_msg == None

    check = Check("testsuite", "check1", 0, "msg")
    assert check.testsuite == "testsuite"
    assert check.id == "testsuite.check1"
    assert check.status == False
    assert check.error_msg == "msg"

    check = Check("testsuite", "check1", 1, "msg")
    assert check.testsuite == "testsuite"
    assert check.id == "testsuite.check1"
    assert check.status == True
    assert check.error_msg == "msg"

def test_Check_to_str():
    """Unit test for the to_str method of the Check class

    The covered behaviors are:
        * without status
        * with status
    
    There are no specific checks performed on the output string. The test only runs the function to check for exceptions.
    """
    check = Check("testsuite", "check1")
    check.to_str()

    check = Check("testsuite", "check1", 0, "msg")
    check.to_str()

def test_Check___repr__():
    """Unit test for the __repr__ method of the Check class

    The covered behaviors are:
        * without status
        * with status
    
    There are no specific checks performed on the output string. The test only runs the function to check for exceptions.
    """
    check = Check("testsuite", "check1")
    repr(check)

    check = Check("testsuite", "check1", 0, "msg")
    str(check)

#
# Tests targetting functions from the check module
#

@patch("glob.glob", side_effect=stubbed_glob)
@patch("builtins.open", side_effect=stubbed_open)
def test_import_checks_01(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behavior is no test source file
    """
    checks = import_checks("path")
    assert len(checks) == 0

@patch("glob.glob", side_effect=stubbed_glob)
@patch("builtins.open", side_effect=stubbed_open)
def test_import_checks_02(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behavior is two files with no checks
    """
    stubbed_glob.file_list = ["file1", "file2"]
    stubbed_open.file_contents["file1"] = "content1"
    stubbed_open.file_contents["file2"] = "content2"

    checks = import_checks("path")
    assert len(checks) == 0

@patch("glob.glob", side_effect=stubbed_glob)
@patch("builtins.open", side_effect=stubbed_open)
def test_import_checks_03(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behaviors are:
        * Two files with multiple checks
        * Checks without testcases
        * Checks with testcases
        * Checks with spaces to check the parsing
    """
    stubbed_glob.file_list = ["file1", "file2"]
    stubbed_open.file_contents["file1"] = """
        CHECK("check1", cond, "error message 1");
        CHECK( "testsuite1.check2", cond, "error message 2");
    """
    stubbed_open.file_contents["file2"] = """
        CHECK("check3" , cond, "error message 3");
        CHECK("testsuite2.check4", cond, "error message 4");
    """
    checks = import_checks("path")

    assert len(checks) == 4
    assert checks[0].testsuite == None
    assert checks[0].id == "check1"
    assert checks[1].testsuite == "testsuite1"
    assert checks[1].id == "testsuite1.check2"
    assert checks[2].testsuite == None
    assert checks[2].id == "check3"
    assert checks[3].testsuite == "testsuite2"
    assert checks[3].id == "testsuite2.check4"
    # Two warning message are generated for the missing testsuites
    assert len(log_warn.msgs) == 2

@patch("glob.glob", side_effect=stubbed_glob)
@patch("builtins.open", side_effect=stubbed_open)
def test_import_checks_04(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behavior is missing check id
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        CHECK("", cond, "error message 1");
    """
    with pytest.raises(SystemExit) as e:
        checks = import_checks("path")
        assert len(checks) == 0
        assert len(log_error.msgs) == 1

    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        CHECK("testsuite.", cond, "error message 1");
    """
    with pytest.raises(SystemExit) as e:
        checks = import_checks("path")
        assert len(checks) == 0
        assert len(log_error.msgs) == 2

@patch("glob.glob", side_effect=stubbed_glob)
@patch("builtins.open", side_effect=stubbed_open)
def test_import_checks_05(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behavior is empty testsuite
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        CHECK(".check1", cond, "error message 1");
    """
    with pytest.raises(SystemExit) as e:
        checks = import_checks("path")
        assert len(checks) == 0
        assert len(log_error.msgs) == 1

    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        CHECK(".", cond, "error message 1");
    """
    with pytest.raises(SystemExit) as e:
        checks = import_checks("path")
        assert len(checks) == 0
        assert len(log_error.msgs) == 2

@patch("glob.glob", side_effect=stubbed_glob)
@patch("builtins.open", side_effect=stubbed_open)
def test_import_testdata_01(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behavior is no testdata files
    """
    checks = import_testdata("path")
    assert len(checks) == 0

@patch("glob.glob", side_effect=stubbed_glob)
@patch("builtins.open", side_effect=stubbed_open)
def test_import_testdata_02(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behavior is complete testdata in multiple files
    """
    stubbed_glob.file_list = ["file1", "file2"]
    stubbed_open.file_contents["file1"] = """
        check1;1
        check2;0;error_msg1
    """
    stubbed_open.file_contents["file2"] = """
        check3;0
        check4;0;error_msg2
    """
    checks = import_testdata("path")
    assert len(checks) == 4
