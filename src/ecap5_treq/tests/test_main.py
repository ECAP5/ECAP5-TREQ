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

from ecap5_treq.main import cmd_print_reqs, cmd_print_checks, cmd_print_testdata
from ecap5_treq.config import Config
from ecap5_treq.check import Check
from ecap5_treq.req import Req, ReqStatus
from ecap5_treq.analyse import Analysis
from ecap5_treq.matrix import Matrix
from ecap5_treq.log import log_error, log_warn, log_clear, log_imp

#
# Fixture definitions
#

@pytest.fixture(autouse=True)
def reset():
    log_clear()
    stubbed_import_reqs.reqs = []

#
# Stub side_effect definitions
#
def stubbed_import_reqs(path):
    return stubbed_import_reqs.reqs

def stubbed_import_checks(path):
    return stubbed_import_checks.checks

def stubbed_import_testdata(path):
    return stubbed_import_testdata.testdata

#
# Tests targetting the functions of the main module
#

@patch("ecap5_treq.main.import_reqs", side_effect=stubbed_import_reqs)
def test_cmd_print_reqs(stub_import_reqs):
    """Unit test for the cmd_print_reqs function
    """
    stubbed_import_reqs.reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {}), \
        Req("N_req5", "description5", {}), \
        Req("req6", "description6", {}) \
    ]

    config = Config()
    config.set("spec_dir_path", "path")

    cmd_print_reqs(config)
    stub_import_reqs.assert_called_once_with("path")

@patch("ecap5_treq.main.import_checks", side_effect=stubbed_import_checks)
def test_cmd_print_checks(stub_import_checks):
    """Unit test for the cmd_print_checks function
    """
    stubbed_import_checks.checks = [ \
        Check("testsuite1", "check1"), \
        Check("testsuite2", "check2"), \
        Check("testsuite2", "check3"), \
        Check(None, "check4"), \
        Check(None, "check5") \
    ]

    config = Config()
    config.set("test_dir_path", "path")

    cmd_print_checks(config)
    stub_import_checks.assert_called_once_with("path")

@patch("ecap5_treq.main.import_testdata", side_effect=stubbed_import_testdata)
def test_cmd_print_testdata(stub_import_testdata):
    """Unit test for the cmd_print_testdata function
    """
    stubbed_import_testdata.testdata = [ \
        Check("testsuite1", "check1", 0, "message1"), \
        Check("testsuite2", "check2", 1, None), \
        Check("testsuite2", "check3", 0, "message2"), \
        Check(None, "check4", 1, None), \
        Check("testsuite3", "check6", 1, None) \
    ]

    config = Config()
    config.set("testdata_dir_path", "path")

    cmd_print_testdata(config)
    stub_import_testdata.assert_called_once_with("path")

def test_cmd_prepare_matrix():
    pass

def test_cmd_gen_report():
    pass

def test_cmd_gen_test_result_badge():
    pass

def test_cmd_gen_traceability_result_badge():
    pass

def test_main():
    pass
