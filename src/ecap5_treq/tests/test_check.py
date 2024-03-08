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
import contextlib
from mock import patch, Mock, mock_open, call
import pytest
import io

from ecap5_treq.check import Check, import_checks, import_testdata, process_check_id, process_keyword, process_string
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
    check = Check("testsuite", "testcase", "check1")
    assert check.testsuite == "testsuite"
    assert check.testcase == "testcase"
    assert check.id == "testsuite.testcase.check1"
    assert check.status == None
    assert check.error_msg == None

    check = Check("testsuite", "testcase", "check1", 0, "msg")
    assert check.testsuite == "testsuite"
    assert check.testcase == "testcase"
    assert check.id == "testsuite.testcase.check1"
    assert check.status == False
    assert check.error_msg == "msg"

    check = Check("testsuite", "testcase", "check1", 1, "msg")
    assert check.testsuite == "testsuite"
    assert check.testcase == "testcase"
    assert check.id == "testsuite.testcase.check1"
    assert check.status == True
    assert check.error_msg == "msg"

def test_Check_to_str():
    """Unit test for the to_str method of the Check class

    The covered behaviors are:
        * without status
        * with status
    
    There are no specific checks performed on the output string. The test only runs the function to check for exceptions.
    """
    check = Check("testsuite", "testcase", "check1")
    check.to_str()

    check = Check("testsuite", "testcase", "check1", 0, "msg")
    check.to_str()

def test_Check___repr__():
    """Unit test for the __repr__ method of the Check class

    The covered behaviors are:
        * without status
        * with status
    
    There are no specific checks performed on the output string. The test only runs the function to check for exceptions.
    """
    check = Check("testsuite", "testcase", "check1")
    repr(check)

    check = Check("testsuite", "testcase", "check1", 0, "msg")
    str(check)

def test_Check___eq__():
    """Unit test for the __eq__ method of the Check class
    """
    check = Check("testsuite1", "testcase1", "check1", 1, "msg1")
    other = Check("testsuite1", "testcase1", "check1", 1, "msg1")
    assert check == other

    check = Check("testsuite1", "testcase1", "check1", 1, "msg1")
    other = Check("testsuite1", "testcase1", "check1", 1, "msg2")
    assert check != other

    check = Check("testsuite1", "testcase1", "check1", 1, "msg1")
    other = Check("testsuite1", "testcase1", "check1", 0, "msg1")
    assert check != other

    check = Check("testsuite1", "testcase1", "check1", 1, "msg1")
    other = Check("testsuite1", "testcase1", "check2", 1, "msg1")
    assert check != other

    check = Check("testsuite1", "testcase1", "check1", 1, "msg1")
    other = Check("testsuite1", "testcase2", "check1", 1, "msg1")
    assert check != other

    check = Check("testsuite1", "testcase1", "check1", 1, "msg1")
    other = Check("testsuite2", "testcase1", "check1", 1, "msg1")
    assert check != other

    check = Check("testsuite1", "testcase1", "check1", 1, "msg1")
    other = "foo"
    assert check != other

#
# Tests targetting functions from the check module
#

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_import_checks_01(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behavior is no test source file
    """
    checks = import_checks("path")
    assert len(checks) == 0

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_import_checks_02(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behavior is two files with no checks
    """
    stubbed_glob.file_list = ["file1", "file2"]
    stubbed_open.file_contents["file1"] = "content1"
    stubbed_open.file_contents["file2"] = "content2"

    checks = import_checks("path")
    assert len(checks) == 0

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_import_checks_03(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behaviors are:
        * Two files with multiple checks
        * Checks with spaces to check the parsing
    """
    stubbed_glob.file_list = ["file1", "file2"]
    stubbed_open.file_contents["file1"] = """
        CHECK("testsuite1.testcase2.check1", cond, "error message 1");
        CHECK( "testsuite1.testcase1.check2", cond, "error message 2");
    """
    stubbed_open.file_contents["file2"] = """
        CHECK("testsuite2.testcase3.check3" , cond, "error message 3");
        CHECK("testsuite2.testcase1.check4" , cond, "error message 4");
    """
    checks = import_checks("path")

    assert len(checks) == 4
    assert checks[0].testsuite == "testsuite1"
    assert checks[0].testcase == "testcase2"
    assert checks[0].id == "testsuite1.testcase2.check1"
    assert checks[1].testsuite == "testsuite1"
    assert checks[1].testcase == "testcase1"
    assert checks[1].id == "testsuite1.testcase1.check2"
    assert checks[2].testsuite == "testsuite2"
    assert checks[2].testcase == "testcase3"
    assert checks[2].id == "testsuite2.testcase3.check3"
    assert checks[3].testsuite == "testsuite2"
    assert checks[3].testcase == "testcase1"
    assert checks[3].id == "testsuite2.testcase1.check4"
    assert len(log_error.msgs) == 0

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_import_checks_04(stub_glob, stub_open):
    """Unit test for the import_check function

    The covered behaviors are:
      - Missing testsuite
      - Missing testcase
      - Missing shortid
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        CHECK("", cond, "error message 1");
        CHECK("testsuite1", cond, "error message 1");
        CHECK("testsuite2.", cond, "error message 1");
        CHECK("testsuite2.testcase1", cond, "error message 1");
        CHECK("testsuite2.testcase1.", cond, "error message 1");
        CHECK(".testcase1.", cond, "error message 1");
        CHECK("testsuite2..shortid1", cond, "error message 1");
        CHECK("..shortid1", cond, "error message 1");
        CHECK("", cond, "error message 1");
    """
    with pytest.raises(SystemExit) as e:
        checks = import_checks("path")
        assert len(checks) == 0
        assert len(log_error.msgs) == 9

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_import_testdata_01(stub_glob, stub_open):
    """Unit test for the import_testdata function

    The covered behavior is no testdata files
    """
    checks = import_testdata("path")
    assert len(checks) == 0

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_import_testdata_02(stub_glob, stub_open):
    """Unit test for the import_testdata function

    The covered behavior is complete testdata in multiple files
    """
    stubbed_glob.file_list = ["file1", "file2"]
    stubbed_open.file_contents["file1"] = """
        testsuite1.testcase1.check1;1
        testsuite1.testcase2.check2;0;error_msg1
    """
    stubbed_open.file_contents["file2"] = """
        testsuite2.testcase3.check3;0
        testsuite3.testcase4.check4;0;error_msg2
    """
    checks = import_testdata("path")

    assert len(checks) == 4
    assert checks[0].testsuite == "testsuite1"
    assert checks[0].testcase == "testcase1"
    assert checks[0].id == "testsuite1.testcase1.check1"
    assert checks[0].status == True
    assert checks[0].error_msg == None

    assert checks[1].testsuite == "testsuite1"
    assert checks[1].testcase == "testcase2"
    assert checks[1].id == "testsuite1.testcase2.check2"
    assert checks[1].status == False
    assert checks[1].error_msg == "error_msg1"

    assert checks[2].testsuite == "testsuite2"
    assert checks[2].testcase == "testcase3"
    assert checks[2].id == "testsuite2.testcase3.check3"
    assert checks[2].status == False
    assert checks[2].error_msg == None

    assert checks[3].testsuite == "testsuite3"
    assert checks[3].testcase == "testcase4"
    assert checks[3].id == "testsuite3.testcase4.check4"
    assert checks[3].status == False
    assert checks[3].error_msg == "error_msg2"

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_import_testdata_03(stub_glob, stub_open):
    """Unit test for the import_testdata function

    The covered behaviors are:
      - Missing testsuite
      - Missing testcase
      - Missing shortid
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        testsuite1;1
        testsuite2.;1
        testsuite2.testcase1;1
        testsuite2.testcase1.;1
        .testcase1.;1
        testsuite2..shortid1;0;error_msg
        ..shortid1;1
    """
    with pytest.raises(SystemExit) as e:
        checks = import_testdata("path")
        assert len(checks) == 0
        assert len(log_error.msgs) == 9

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_import_testdata_04(stub_glob, stub_open):
    """Unit test for the import_testdata function

    The covered behavior is incomplete testdata
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        testsuite1.testcase1.check1
    """
    with pytest.raises(SystemExit) as e:
        checks = import_testdata("path")
        assert len(log_error.msgs) == 1

    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        testsuite1.testcase2.check1;
    """
    with pytest.raises(SystemExit) as e:
        checks = import_testdata("path")
        assert len(log_error.msgs) == 1

def test_process_check_id_01():
    """Unit test for the process_check_id function

    The covered behaviors are:
        * missing testsuite
        * missing testcase
        * missing shortid
    """
    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id("")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id("testsuite")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id("testsuite.testcase")
        assert len(log_error.msgs) == 1

def test_process_check_id_02():
    """Unit test for the process_check_id function

    The covered behaviors are:
        * empty testsuite
        * empty testcase
        * empty shortid
    """
    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id("..")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id("testsuite..")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id(".testcase.")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id("..shortid")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id("testsuite.testcase.")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id("testsuite..shortid")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        testsuite, testcase, shortid = process_check_id(".testcase.shortid")
        assert len(log_error.msgs) == 1

def test_process_keyword_01():
    """Unit test for the process_keyword function

    The covered behaviors are :
        * Cur equal zero
        * Cur greater than zero
        * Keyword without spaces
        * Keyword with spaces
    """
    cur = process_keyword(0, "CHECK(\"id\")")
    assert cur == 6

    cur = process_keyword(5, "     CHECK (  \"id\")")
    assert cur == 14

def test_process_keyword_02():
    """Unit test for the process_keyword function

    The covered behavior is syntax error in keyword
    """
    with pytest.raises(SystemExit) as e:
        cur = process_keyword(0, "CHECK(id\")")
        # A syntax error shall be raised
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        # A syntax error shall be raised
        cur = process_keyword(0, "CHECK(id)")
        assert len(log_error.msgs) == 1

def test_process_string_01():
    """Unit test for the process_string function

    The covered behaviors are:
        * Cur equal zero
        * Cur greater than zero
        * Valid string
    """
    cur, result = process_string(0, "\"string content\"")
    assert cur == 16
    assert result == "string content"

    cur, result = process_string(5, "     \"string content\"")
    assert cur == 21
    assert result == "string content"

def test_process_string_02():
    """Unit test for the process_string function

    The covered behaviors are:
        * Missing starting \"
        * Missing closing \"
    """
    with pytest.raises(SystemExit) as e:
        cur, result = process_string(0, "string content\"")
        assert len(log_error.msgs) == 1

    with pytest.raises(SystemExit) as e:
        cur, result = process_string(0, "\"string content")
        assert len(log_error.msgs) == 2
