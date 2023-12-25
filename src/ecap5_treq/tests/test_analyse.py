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

from ecap5_treq.check import Check
from ecap5_treq.analyse import Analysis
from ecap5_treq.matrix import Matrix
from ecap5_treq.log import log_error, log_warn, log_clear

#
# Fixture definitions
#

@pytest.fixture(autouse=True)
def reset():
    log_clear()

#
# Tests targetting Check class
#

@patch.object(Analysis, "analyse")
def test_Analysis_constructor(stub_Analysis_analyse):
    """Unit test for the constructor of the Analysis class
    """
    analysis = Analysis([], [], [], None)
    stub_Analysis_analyse.assert_called_once()

@patch.object(Analysis, "analyse_tests")
@patch.object(Analysis, "analyse_traceability")
@patch.object(Analysis, "analyse_consistency")
def test_Analysis_analyse(stub_Analysis_analyse_tests, stub_Analysis_analyse_traceability, stub_Analysis_analyse_consistency):
    """Unit test for the analyse method of the Analysis class
    """
    analysis = Analysis([], [], [], None)
    stub_Analysis_analyse_tests.assert_called_once()
    stub_Analysis_analyse_traceability.assert_called_once()
    stub_Analysis_analyse_consistency.assert_called_once()

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_tests_01(stub_analyse):
    """Unit test for the analyse_tests method of the Analysis class

    The covered behavior is no checks.

    The analyse method is stubbed so the analyse_tests is called on its own.
    """
    checks = []
    testdata = []
    analysis = Analysis([], checks, testdata, None) 
    analysis.analyse_tests()

    assert analysis.num_successfull_checks == 0
    assert analysis.num_failed_checks == 0
    assert analysis.check_status_by_check_id == {}
    assert analysis.testsuites == {}
    assert analysis.no_testsuite == []
    assert analysis.skipped_checks == []
    assert analysis.unknown_checks == []
    assert analysis.test_result == 0

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_tests_02(stub_analyse):
    """Unit test for the analyse_tests method of the Analysis class

    The covered behavior is checks with no testdata
    """
    checks = [Check("testsuite1", "check1"), Check("testsuite2", "check2"), Check(None, "check3"), Check(None, "check4")]
    testdata = []
    analysis = Analysis([], checks, testdata, None) 

    analysis.analyse_tests()

    assert analysis.num_successfull_checks == 0
    assert analysis.num_failed_checks == 0
    assert analysis.check_status_by_check_id == {}
    assert analysis.testsuites == {}
    assert analysis.no_testsuite == []
    assert analysis.skipped_checks == checks
    assert analysis.unknown_checks == []
    assert analysis.test_result == 0

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_tests_03(stub_analyse):
    """Unit test for the analyse_tests method of the Analysis class

    The covered behavior is checks with testdata with:
        * Testsuite with one check
        * Testsuite with multiple checks
        * Checks with no testsuite
        * Checks with true status
        * Checks with false status
        * Checks skipped
        * Checks unknown
    """
    checks = [ \
        Check("testsuite1", "check1"), \
        Check("testsuite2", "check2"), \
        Check("testsuite2", "check3"), \
        Check(None, "check4"), \
        Check(None, "check5") \
    ]
    testdata = [ \
        Check("testsuite1", "check1", 0, "message1"), \
        Check("testsuite2", "check2", 1, None), \
        Check("testsuite2", "check3", 0, "message2"), \
        Check(None, "check4", 1, None), \
        Check("testsuite3", "check6", 1, None) \
    ]
    analysis = Analysis([], checks, testdata, None) 

    analysis.analyse_tests()

    assert analysis.num_successfull_checks == 3
    assert analysis.num_failed_checks == 2
    assert analysis.check_status_by_check_id == { \
        "testsuite1.check1":False, \
        "testsuite2.check2":True, \
        "testsuite2.check3":False, \
        "check4":True, \
        "testsuite3.check6":True \
    }
    assert analysis.testsuites == { \
        "testsuite1": [ \
            Check("testsuite1", "check1", 0, "message1") \
        ], \
        "testsuite2":[ \
            Check("testsuite2", "check2", 1, None), \
            Check("testsuite2", "check3", 0, "message2") \
        ], \
        "testsuite3":[ \
            Check("testsuite3", "check6", 1, None) \
        ] \
    }
    assert analysis.no_testsuite == [ \
        Check(None, "check4", 1, None) \
    ]
    assert analysis.skipped_checks == [ \
        Check(None, "check5") \
    ]
    assert analysis.unknown_checks == [ \
        Check("testsuite3", "check6", 1, None)
    ]
    assert analysis.test_result == 60

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_traceability_01(stub_analyse):
    """Unit test for the analyse_traceability method of the Analysis class

    The covered behavior is no reqs.

    The analyse method is stubbed so the analyse_traceability is called on its own.
    """
    reqs = []
    matrix = Matrix() 
    analysis = Analysis(reqs, [], [], matrix)
    analysis.analyse_traceability()

    assert analysis.reqs_covering_reqs == {}
    assert analysis.checks_covering_reqs == {}
    assert analysis.ids_reqs_untraceable == []
    assert analysis.num_covered_reqs == 0
    assert analysis.num_untraceable_reqs == 0
    assert analysis.num_uncovered_reqs == 0
    assert analysis.user_reqs == []
    assert analysis.external_interface_reqs == []
    assert analysis.functional_reqs == []
    assert analysis.design_reqs == []
    assert analysis.non_functional_reqs == []
    assert analysis.other_reqs == []
    assert analysis.traceability_result == 0

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_traceability_02(stub_analyse):
    """Unit test for the analyse_traceability method of the Analysis class

    The covered behavior is reqs with no derivedfrom.

    The analyse method is stubbed so the analyse_traceability is called on its own.
    """

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_traceability_03(stub_analyse):
    """Unit test for the analyse_traceability method of the Analysis class

    The covered behavior is reqs with derivedfrom.

    The analyse method is stubbed so the analyse_traceability is called on its own.
    """
