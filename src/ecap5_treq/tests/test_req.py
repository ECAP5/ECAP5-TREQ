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

from ecap5_treq.req import Req, ReqStatus, import_reqs, rst_import_reqs, tex_import_reqs, tex_process_keyword, tex_process_matching_token, tex_process_options
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
# Tests targetting Req class
#

def test_Req_constructor_01():
    """Unit test for the constructor of the Req class

    The covered behaviors are:
        * id without escaped chars
        * id with escaped chars
        * no options
        * with derivedfrom options containing one value
        * with derivedfrom options containing multiple value
        * with allocation options containing one value
        * with allocation options containing multiple value
        * with other options
    """
    req = Req("req1", "description", None)
    assert req.id == "req1"
    assert req.description == "description"
    assert req.status == ReqStatus.UNCOVERED
    assert req.result == 0

    req = Req("req1\\_foo", "description", None)
    assert req.id == "req1_foo"
    assert req.description == "description"
    assert req.status == ReqStatus.UNCOVERED
    assert req.derived_from == None
    assert req.allocation == None
    assert req.result == 0

    req = Req("req1\\_foo", "description", {"other": ["content1"]})
    assert req.id == "req1_foo"
    assert req.description == "description"
    assert req.status == ReqStatus.UNCOVERED
    assert req.derived_from == None
    assert req.allocation == None
    assert req.result == 0

    req = Req("req1\\_foo", "description", {"derivedfrom": ["req2"]})
    assert req.id == "req1_foo"
    assert req.description == "description"
    assert req.status == ReqStatus.UNCOVERED
    assert req.derived_from == ["req2"]
    assert req.allocation == None
    assert req.result == 0

    req = Req("req1\\_foo", "description", {"derivedfrom": ["req2", "req3"]})
    assert req.id == "req1_foo"
    assert req.description == "description"
    assert req.status == ReqStatus.UNCOVERED
    assert req.derived_from == ["req2", "req3"]
    assert req.allocation == None
    assert req.result == 0

    req = Req("req1\\_foo", "description", {"other": ["content1", "content2"], "derivedfrom": ["req2"]})
    assert req.id == "req1_foo"
    assert req.description == "description"
    assert req.status == ReqStatus.UNCOVERED
    assert req.derived_from == ["req2"]
    assert req.allocation == None
    assert req.result == 0

    req = Req("req1\\_foo", "description", {"other": ["content1", "content2"], "derivedfrom": ["req2"]}, ReqStatus.COVERED)
    assert req.id == "req1_foo"
    assert req.description == "description"
    assert req.status == ReqStatus.COVERED
    assert req.derived_from == ["req2"]
    assert req.allocation == None
    assert req.result == 0

    req = Req("req1\\_foo", "description", {"other": ["content1", "content2"], "derivedfrom": ["req2"]}, ReqStatus.COVERED, 85)
    assert req.id == "req1_foo"
    assert req.description == "description"
    assert req.status == ReqStatus.COVERED
    assert req.derived_from == ["req2"]
    assert req.allocation == None
    assert req.result == 85
    
    req = Req("req1\\_foo", "description", {"allocation": ["content1"]})
    assert req.id == "req1_foo"
    assert req.description == "description"
    assert req.status == ReqStatus.UNCOVERED
    assert req.derived_from == None
    assert req.allocation == ["content1"]
    assert req.result == 0

def test_Req_to_str():
    """Unit test for the to_str method of the Req class

    There are no specific checks performed on the output string. The test only runs the function to check for exceptions.
    """
    req = Req("req1\\_foo", None, None)
    req.to_str()

    req = Req("req1\\_foo", "description", None)
    req.to_str()

    req = Req("req1\\_foo", "description", {"derivedfrom": ["req2"]})
    req.to_str()

    req = Req("req1\\_foo", "description", {"allocation": ["module2"]})
    req.to_str()

    req = Req("req1\\_foo", "description", {"other": ["content1", "content2"], "derivedfrom": ["req2", "req3"]})
    req.to_str()

def test_Req___repr__():
    """Unit test for the __repr__ method of the Req class

    There are no specific checks performed on the output string. The test only runs the function to check for exceptions.
    """
    req = Req("req1\\_foo", None, None)
    repr(req)

    req = Req("req1\\_foo", "description", None)
    repr(req)

    req = Req("req1\\_foo", "description", {"derivedfrom": ["req2"]})
    repr(req)

    req = Req("req1\\_foo", "description", {"allocation": ["module2"]})
    repr(req)

    req = Req("req1\\_foo", "description", {"other": ["content1", "content2"], "derivedfrom": ["req2", "req3"]})
    repr(req)

def test_Req___str__():
    """Unit test for the __str__ method of the Req class

    There are no specific checks performed on the output string. The test only runs the function to check for exceptions.
    """
    req = Req("req1\\_foo", None, None)
    str(req)

    req = Req("req1\\_foo", "description", None)
    str(req)

    req = Req("req1\\_foo", "description", {"derivedfrom": ["req2"]})
    str(req)

    req = Req("req1\\_foo", "description", {"allocation": ["module2"]})
    str(req)

    req = Req("req1\\_foo", "description", {"other": ["content1", "content2"], "derivedfrom": ["req2", "req3"]})
    str(req)

def test_Req___eq__():
    """Unit test for the __eq__ method of the Req class
    """
    req = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    other = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    assert req == other

    req = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    other = Req("req2", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    assert req != other

    req = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    other = Req("req1", "description2", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    assert req != other

    req = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    other = Req("req1", "description1", {"derivedfrom": ["dreq2", "req2"], "allocation": ["module1", "module2"]})
    assert req != other

    req = Req("req1", "description1", {"derivedfrom": ["dreq1", "req1"], "allocation": ["module1", "module2"]})
    other = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    assert req != other

    req = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module1"]})
    other = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    assert req != other

    req = Req("req1", "description1", {"derivedfrom": ["dreq1", "req2"], "allocation": ["module1", "module2"]})
    other = "foo"
    assert req != other

#
# Tests targetting functions in req module
#

@patch("ecap5_treq.req.rst_import_reqs", return_value=["val"])
def test_import_reqs_01(stub_rst_import_reqs):
    """Unit test for the import_reqs function

    The covered behavior is RST format
    """
    reqs = import_reqs("path1", "RST")
    stub_rst_import_reqs.assert_called_once_with("path1")
    assert reqs == ["val"]

@patch("ecap5_treq.req.tex_import_reqs", return_value=["val"])
def test_import_reqs_02(stub_tex_import_reqs):
    """Unit test for the import_reqs function

    The covered behavior is TEX format
    """
    reqs = import_reqs("path1", "TEX")
    stub_tex_import_reqs.assert_called_once_with("path1")
    assert reqs == ["val"]

def test_import_reqs_03():
    """Unit test for the import_reqs function

    The covered behavior is unknown format
    """
    with pytest.raises(SystemExit) as e:
        reqs = import_reqs("path1", "unknown")
        assert len(log_error.msgs) == 1

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_rst_import_reqs_01(stub_glob, stub_open):
    """Unit test for the rst_import_reqs function

    The covered behavior is no specification source file
    """
    reqs = rst_import_reqs("path")
    assert len(reqs) == 0

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_rst_import_reqs_02(stub_glob, stub_open):
    """Unit test for the rst_import_reqs function

    The covered behavior is two files with no reqs
    """
    stubbed_glob.file_list = ["file1", "file2"]
    stubbed_open.file_contents["file1"] = "content1"
    stubbed_open.file_contents["file2"] = "content2"

    reqs = rst_import_reqs("path")
    assert len(reqs) == 0

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_rst_import_reqs_03(stub_glob, stub_open):
    """Unit test for the rst_import_reqs function

    The covered behaviors are:
        * Two files with multiple reqs
        * Req without option
        * Req with options
    """
    stubbed_glob.file_list = ["file1", "file2", "file3"]
    stubbed_open.file_contents["file1"] = """
        \\req{req1}{description1}
.. requirement:: req1
    
    description1

.. requirement:: req2

    description2

.. directive:: ponpon

    ponpon
    """
    stubbed_open.file_contents["file2"] = """
.. requirement:: req3

    description3

.. requirement:: req4
    :option1: content1
    :derivedfrom: req1
    
    description4

    """
    stubbed_open.file_contents["file3"] = """
.. requirement:: req5
    :option1: content1
    :derivedfrom: req1, req2

    description5
    """
    reqs = rst_import_reqs("path")

    assert len(reqs) == 5
    assert reqs[0].id == "req1"
    assert reqs[0].description == "description1"
    assert reqs[0].derived_from == None

    assert reqs[1].id == "req2"
    assert reqs[1].description == "description2"
    assert reqs[1].derived_from == None

    assert reqs[2].id == "req3"
    assert reqs[2].description == "description3"
    assert reqs[2].derived_from == None

    assert reqs[3].id == "req4"
    assert reqs[3].description == "description4"
    assert reqs[3].derived_from == ["req1"]

    assert reqs[4].id == "req5"
    assert reqs[4].description == "description5"
    assert reqs[4].derived_from == ["req1", "req2"]

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_rst_import_reqs_04(stub_glob, stub_open):
    """Unit test for the rst_import_reqs function

    The covered behavior is Req with empty id
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
.. requirement:: 

content
    """
    with pytest.raises(SystemExit) as e:
        reqs = rst_import_reqs("path")
        assert len(log_error.msgs) == 1

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_rst_import_reqs_05(stub_glob, stub_open):
    """Unit test for the rst_import_reqs function

    The covered behavior is Req with missing description
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
.. requirement:: req1
content
    """
    reqs = rst_import_reqs("path")
    assert len(log_warn.msgs) == 1

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_rst_import_reqs_06(stub_glob, stub_open):
    """Unit test for the rst_import_reqs function

    The covered behavior is Req with empty description
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
.. requirement:: req1

content
    """
    reqs = rst_import_reqs("path")
    assert len(log_warn.msgs) == 1

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_tex_import_reqs_01(stub_glob, stub_open):
    """Unit test for the tex_import_reqs function

    The covered behavior is no specification source file
    """
    reqs = tex_import_reqs("path")
    assert len(reqs) == 0

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_tex_import_reqs_02(stub_glob, stub_open):
    """Unit test for the tex_import_reqs function

    The covered behavior is two files with no reqs
    """
    stubbed_glob.file_list = ["file1", "file2"]
    stubbed_open.file_contents["file1"] = "content1"
    stubbed_open.file_contents["file2"] = "content2"

    reqs = tex_import_reqs("path")
    assert len(reqs) == 0

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_tex_import_reqs_03(stub_glob, stub_open):
    """Unit test for the tex_import_reqs function

    The covered behaviors are:
        * Two files with multiple reqs
        * Req without option
        * Req with options
    """
    stubbed_glob.file_list = ["file1", "file2", "file3"]
    stubbed_open.file_contents["file1"] = """
        \\req{req1}{description1}

        \\req{req2}{
            description2
        }

        \\reqponpon{req}{des}
    """
    stubbed_open.file_contents["file2"] = """
        \\req{req3}{description3}

        \\req{req4}{
            description4
        }[option1=content1, derivedfrom=req1]
    """
    stubbed_open.file_contents["file3"] = """
        \\req{req5}{
            description5
        }[option1=content1, derivedfrom={req1, req2}]
    """
    reqs = tex_import_reqs("path")

    assert len(reqs) == 5
    assert reqs[0].id == "req1"
    assert reqs[0].description == "description1"
    assert reqs[0].derived_from == None

    assert reqs[1].id == "req2"
    assert reqs[1].description == "description2"
    assert reqs[1].derived_from == None

    assert reqs[2].id == "req3"
    assert reqs[2].description == "description3"
    assert reqs[2].derived_from == None

    assert reqs[3].id == "req4"
    assert reqs[3].description == "description4"
    assert reqs[3].derived_from == ["req1"]

    assert reqs[4].id == "req5"
    assert reqs[4].description == "description5"
    assert reqs[4].derived_from == ["req1", "req2"]

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_tex_import_reqs_04(stub_glob, stub_open):
    """Unit test for the tex_import_reqs function

    The covered behavior is Req with empty id
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        \\req{}{description}
    """
    with pytest.raises(SystemExit) as e:
        reqs = tex_import_reqs("path")
        assert len(log_error.msgs) == 1

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_tex_import_reqs_05(stub_glob, stub_open):
    """Unit test for the tex_import_reqs function

    The covered behavior is Req with missing description
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        \\req{req1}
    """
    reqs = tex_import_reqs("path")
    assert len(log_warn.msgs) == 1

@patch("builtins.open", side_effect=stubbed_open)
@patch("glob.glob", side_effect=stubbed_glob)
def test_tex_import_reqs_06(stub_glob, stub_open):
    """Unit test for the tex_import_reqs function

    The covered behavior is Req with empty description
    """
    stubbed_glob.file_list = ["file1"]
    stubbed_open.file_contents["file1"] = """
        \\req{req1}{}
    """
    reqs = tex_import_reqs("path")
    assert len(log_warn.msgs) == 1

def test_tex_process_keyword_01():
    """Unit test for the tex_process_keyword function

    The covered behaviors are :
        * Cur equal zero
        * Cur greater than zero
        * Keyword without spaces
        * Keyword with spaces
    """
    cur = tex_process_keyword(0, "\\req{id}")
    assert cur == 4

    cur = tex_process_keyword(5, "     \\req {  id}")
    assert cur == 10

def test_tex_process_keyword_02():
    """Unit test for the tex_process_keyword function

    The covered behavior is syntax error in keyword
    """
    with pytest.raises(SystemExit) as e:
        cur = tex_process_keyword(0, "\\req id}")
        assert len(log_error.msgs) == 1

def test_tex_process_matching_token_01():
    """Unit test for the tex_process_matching_token function

    The covered behaviors are:
        * Cur equal to zero
        * Cur greater than zero
        * only one valid level of tokens
        * multiple valid levels of tokens
        * different sets of tokens
    """
    cur, result = tex_process_matching_token(0, "{content1}", "{", "}")
    assert cur == 10
    assert result == "content1"

    cur, result = tex_process_matching_token(5, "     [content1]", "[", "]")
    assert cur == 15
    assert result == "content1"

    cur, result = tex_process_matching_token(0, "{content1 {second_level} end}", "{", "}")
    assert cur == 29
    assert result == "content1 {second_level} end"

def test_tex_process_matching_token_02():
    """Unit test for the tex_process_matching_token function

    The covered behaviors are:
        * missing opening token in one level
        * missing closing token in one level
        * missing opening token in multiple levels
        * missing closing token in multiple levels
    """
    cur, result = tex_process_matching_token(0, "content1", "{", "}")
    assert cur == 0
    assert result == None

    with pytest.raises(SystemExit) as e:
        cur, result = tex_process_matching_token(0, "{content1", "{", "}")
        assert len(log_error.msgs) == 1

    cur, result = tex_process_matching_token(0, "content1 {content2}}", "{", "}")
    assert cur == 0
    assert result == None

    with pytest.raises(SystemExit) as e:
        cur, result = tex_process_matching_token(0, "{content1 {content2} end", "{", "}")
        assert len(log_error.msgs) == 2

def test_tex_process_options_01():
    """Unit test for the tex_process_options function

    The covered behaviors are:
        * Empty options
        * multiple options with single values
        * multiple options with complex values
    """
    options = tex_process_options("")
    assert len(options.keys()) == 0

    options = tex_process_options("option1=content1, option2=content2")
    assert len(options.keys()) == 2
    assert options["option1"] == ["content1"]
    assert options["option2"] == ["content2"]

    options = tex_process_options("option1={content1, content2, content3}, option2={content3 = content4}")
    assert len(options.keys()) == 2
    assert options["option1"] == ["content1", "content2", "content3"]
    assert options["option2"] == ["content3 = content4"]

def test_tex_process_options_02():
    """Unit test for the tex_process_options function

    The covered behavior is syntax error in option
    """
    with pytest.raises(SystemExit) as e:
        options = tex_process_options("option1, option2=content2")
        assert len(log_error.msgs) == 1
