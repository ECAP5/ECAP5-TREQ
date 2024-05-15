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

from ecap5_treq.check import Check
from ecap5_treq.req import Req, ReqStatus
from ecap5_treq.analysis import Analysis
from ecap5_treq.matrix import Matrix
from ecap5_treq.log import log_error, log_warn, log_clear, log_imp

#
# Fixture definitions
#

@pytest.fixture(autouse=True)
def reset():
    log_clear()

#
# Tests targetting Analysis class
#

@patch.object(Analysis, "analyse")
def test_Analysis_constructor(stub_Analysis_analyse):
    """Unit test for the constructor of the Analysis class
    """
    analysis = Analysis([], [], [], None)
    stub_Analysis_analyse.assert_called_once()

@patch.object(Analysis, "analyse_consistency")
@patch.object(Analysis, "analyse_traceability")
@patch.object(Analysis, "analyse_tests")
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
    assert analysis.num_successfull_unknown_checks == 0
    assert analysis.num_failed_unknown_checks == 0
    assert analysis.check_status_by_check_id == {}
    assert analysis.testsuites == {}
    assert analysis.num_checks_in_testsuites == {}
    assert analysis.skipped_checks == []
    assert analysis.unknown_checks == []
    assert analysis.test_result == 0

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_tests_02(stub_analyse):
    """Unit test for the analyse_tests method of the Analysis class

    The covered behavior is checks with no testdata
    """
    checks = [Check("testsuite1", "testcase1", "check1"), Check("testsuite2", "testcase1", "check2"), Check("testsuite2", "testcase1", "check3"), Check("testsuite1", "testcase1", "check4")]
    testdata = []
    analysis = Analysis([], checks, testdata, None) 

    analysis.analyse_tests()

    assert analysis.num_successfull_checks == 0
    assert analysis.num_failed_checks == 0
    assert analysis.num_successfull_unknown_checks == 0
    assert analysis.num_failed_unknown_checks == 0
    assert analysis.check_status_by_check_id == {}
    assert analysis.testsuites == {}
    assert analysis.num_checks_in_testsuites == {}
    assert analysis.skipped_checks == checks
    assert analysis.unknown_checks == []
    assert analysis.test_result == 0

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_tests_03(stub_analyse):
    """Unit test for the analyse_tests method of the Analysis class

    The covered behavior is checks with testdata with:
        * Testsuite with one testcase and one check
        * Testsuite with one testcase and multiple checks
        * Testsuite with multiple testcases and one check
        * Testsuite with multiple testcases and multiple checks
        * Checks with true status
        * Checks with false status
        * Checks skipped
        * Checks unknown
    """
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite2", "testcase1", "check2"), \
        Check("testsuite2", "testcase1", "check3"), \
        Check("testsuite3", "testcase1", "check4"), \
        Check("testsuite3", "testcase2", "check5"), \
        Check("testsuite4", "testcase1", "check5"), \
        Check("testsuite4", "testcase1", "check6"), \
        Check("testsuite4", "testcase2", "check7") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "message1"), \
        Check("testsuite2", "testcase1", "check2", 1, None), \
        Check("testsuite2", "testcase1", "check3", 0, "message2"), \
        Check("testsuite3", "testcase1", "check4", 1, None), \
        Check("testsuite3", "testcase2", "check9", 1, None), \
        Check("testsuite3", "testcase2", "check10", 0, "msg1"), \
        Check("testsuite3", "testcase2", "check11", 0, "msg2") \
    ]
    analysis = Analysis([], checks, testdata, None) 

    analysis.analyse_tests()

    assert analysis.num_successfull_checks == 3
    assert analysis.num_failed_checks == 4
    assert analysis.num_successfull_unknown_checks == 1
    assert analysis.num_failed_unknown_checks == 2
    assert analysis.check_status_by_check_id == { \
        "testsuite1.testcase1.check1":False, \
        "testsuite2.testcase1.check2":True, \
        "testsuite2.testcase1.check3":False, \
        "testsuite3.testcase1.check4":True, \
        "testsuite3.testcase2.check9":True, \
        "testsuite3.testcase2.check10":False, \
        "testsuite3.testcase2.check11":False \
    }
    assert analysis.testsuites == { \
        "testsuite1": { \
            "testcase1": [ \
                Check("testsuite1", "testcase1", "check1", 0, "message1") \
            ], \
        }, \
        "testsuite2": { \
            "testcase1": [ \
                Check("testsuite2", "testcase1", "check2", 1, None), \
                Check("testsuite2", "testcase1", "check3", 0, "message2") \
            ] \
        }, \
        "testsuite3": { \
            "testcase1": [ \
                Check("testsuite3", "testcase1", "check4", 1, None) \
            ], \
            "testcase2": [ \
                Check("testsuite3", "testcase2", "check9", 1, None), \
                Check("testsuite3", "testcase2", "check10", 0, "msg1"), \
                Check("testsuite3", "testcase2", "check11", 0, "msg2") \
            ] \
        } \
    }
    assert analysis.num_checks_in_testsuites == {
        "testsuite1": 1,
        "testsuite2": 2,
        "testsuite3": 4
    }
    assert analysis.skipped_checks == [ \
        Check("testsuite3", "testcase2", "check5"), \
        Check("testsuite4", "testcase1", "check5"), \
        Check("testsuite4", "testcase1", "check6"), \
        Check("testsuite4", "testcase2", "check7") \
    ]
    assert analysis.unknown_checks == [ \
        Check("testsuite3", "testcase2", "check9", 1, None), \
        Check("testsuite3", "testcase2", "check10", 0, "msg1"), \
        Check("testsuite3", "testcase2", "check11", 0, "msg2") \
    ]
    assert analysis.test_result == 37

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

    assert analysis.ids_reqs_covering_reqs == {}
    assert analysis.ids_checks_covering_reqs == {}
    assert analysis.justif_reqs_untraceable == {}
    assert analysis.num_covered_reqs == 0
    assert analysis.num_untraceable_reqs == 0
    assert analysis.num_uncovered_reqs == 0
    assert analysis.num_allocated_reqs == 0
    assert analysis.user_reqs == []
    assert analysis.external_interface_reqs == []
    assert analysis.functional_reqs == []
    assert analysis.architecture_reqs == []
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
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {}), \
        Req("F_req3", "description3", {}), \
        Req("A_req7", "description7", {}), \
        Req("D_req4", "description4", {}), \
        Req("N_req5", "description5", {}), \
        Req("req6", "description6", {}) \
    ]
    matrix = Matrix()
    analysis = Analysis(reqs, [], [], matrix)
    analysis.analyse_traceability()

    assert analysis.ids_reqs_covering_reqs == {}
    assert analysis.ids_checks_covering_reqs == {}
    assert analysis.justif_reqs_untraceable == {}
    assert analysis.num_covered_reqs == 0
    assert analysis.num_untraceable_reqs == 0
    assert analysis.num_uncovered_reqs == 7
    assert analysis.num_allocated_reqs == 0
    assert analysis.user_reqs == [ \
        Req("U_req1", "description1", {}) \
    ]
    assert analysis.external_interface_reqs == [ \
        Req("I_req2", "description2", {}) \
    ]
    assert analysis.functional_reqs == [ \
        Req("F_req3", "description3", {}) \
    ]
    assert analysis.architecture_reqs == [ \
        Req("A_req7", "description7", {}) \
    ]
    assert analysis.design_reqs == [ \
        Req("D_req4", "description4", {}) \
    ]
    assert analysis.non_functional_reqs == [ \
        Req("N_req5", "description5", {}) \
    ]
    assert analysis.other_reqs == [ \
        Req("req6", "description6", {}) \
    ]
    assert analysis.traceability_result == 0

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_traceability_03(stub_analyse):
    """Unit test for the analyse_traceability method of the Analysis class

    The covered behavior is reqs with derivedfrom, allocation and checks covering reqs

    The analyse method is stubbed so the analyse_traceability is called on its own.
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2", "req8"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"], "allocation": ["module2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {"allocation": ["module1", "module2"]}), \
        Req("req8", "description8", {}), \
        Req("A_req9", "description9", {}), \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6", "A_req9"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)
    analysis.analyse_traceability()

    assert analysis.ids_reqs_covering_reqs == { \
        "U_req1": [ "I_req2" ], \
        "I_req2": [ "D_req4", "N_req5" ], \
        "req8": [ "D_req4" ] \
    }
    assert analysis.ids_checks_covering_reqs == { \
        "F_req3": [ "testsuite1.testcase1.check1" ], \
        "D_req4": [ "testsuite1.testcase1.check2" ], \
        "req6": [ "testsuite1.testcase1.check2" ], \
        "A_req9" : [ "testsuite1.testcase1.check2" ] \
    }
    assert analysis.justif_reqs_untraceable == { \
        "req7": "just1" \
    }
    assert analysis.num_covered_reqs == 7
    assert analysis.num_untraceable_reqs == 1
    assert analysis.num_uncovered_reqs == 1
    assert analysis.num_allocated_reqs == 2
    assert analysis.user_reqs == [ \
        Req("U_req1", "description1", {}, ReqStatus.COVERED) \
    ]
    assert analysis.external_interface_reqs == [ \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}, ReqStatus.COVERED) \
    ]
    assert analysis.functional_reqs == [ \
        Req("F_req3", "description3", {}, ReqStatus.COVERED) \
    ]
    assert analysis.architecture_reqs == [ \
        Req("A_req9", "description9", {}, ReqStatus.COVERED, 100) \
    ]
    assert analysis.design_reqs == [ \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2", "req8"]}, ReqStatus.COVERED, 100) \
    ]
    assert analysis.non_functional_reqs == [ \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"], "allocation": ["module2"]}, ReqStatus.UNCOVERED) \
    ]
    assert analysis.other_reqs == [ \
        Req("req6", "description6", {}, ReqStatus.COVERED, 100), \
        Req("req7", "description7", {"allocation": ["module1", "module2"]}, ReqStatus.UNTRACEABLE), \
        Req("req8", "description8", {}, ReqStatus.COVERED), \
    ]
    assert analysis.traceability_result == 55

@patch.object(Analysis, "analyse")
def test_Analysis_analyse_traceability_04(stub_analyse):
    """Unit test for the analyse_traceability method of the Analysis class

    The covered behavior is allocation disabled

    The analyse method is stubbed so the analyse_traceability is called on its own.
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2", "req8"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"], "allocation": ["module2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {"allocation": ["module1", "module2"]}), \
        Req("req8", "description8", {}), \
        Req("A_req9", "description9", {}), \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6", "A_req9"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix, False)
    analysis.analyse_traceability()

    assert analysis.ids_reqs_covering_reqs == { \
        "U_req1": [ "I_req2" ], \
        "I_req2": [ "D_req4", "N_req5" ], \
        "req8": [ "D_req4" ] \
    }
    assert analysis.ids_checks_covering_reqs == { \
        "F_req3": [ "testsuite1.testcase1.check1" ], \
        "D_req4": [ "testsuite1.testcase1.check2" ], \
        "req6": [ "testsuite1.testcase1.check2" ], \
        "A_req9" : [ "testsuite1.testcase1.check2" ] \
    }
    assert analysis.justif_reqs_untraceable == { \
        "req7": "just1" \
    }
    assert analysis.num_covered_reqs == 7
    assert analysis.num_untraceable_reqs == 1
    assert analysis.num_uncovered_reqs == 1
    assert analysis.num_allocated_reqs == 2
    assert analysis.user_reqs == [ \
        Req("U_req1", "description1", {}, ReqStatus.COVERED) \
    ]
    assert analysis.external_interface_reqs == [ \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}, ReqStatus.COVERED) \
    ]
    assert analysis.functional_reqs == [ \
        Req("F_req3", "description3", {}, ReqStatus.COVERED) \
    ]
    assert analysis.architecture_reqs == [ \
        Req("A_req9", "description9", {}, ReqStatus.COVERED, 100) \
    ]
    assert analysis.design_reqs == [ \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2", "req8"]}, ReqStatus.COVERED, 100) \
    ]
    assert analysis.non_functional_reqs == [ \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"], "allocation": ["module2"]}, ReqStatus.UNCOVERED) \
    ]
    assert analysis.other_reqs == [ \
        Req("req6", "description6", {}, ReqStatus.COVERED, 100), \
        Req("req7", "description7", {"allocation": ["module1", "module2"]}, ReqStatus.UNTRACEABLE), \
        Req("req8", "description8", {}, ReqStatus.COVERED), \
    ]
    assert analysis.traceability_result == 88

def test_Analysis_analyse_consistency_01():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Matrix up to date
        * All requirements used in the matrix exist
        * No check is traced to an untraceable requirement
        * No requirement is traced multiple times to the same check
        * No duplicate requirement id
        * All requirements specified in the derivedfrom option exist
        * No requirement has itself in its derivedfrom option
        * No duplicate check id
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 0
    assert len(log_error.msgs) == 0

def test_Analysis_analyse_consistency_02():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Matrix is NOT up to date
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2"), \
        Check("testsuite1", "testcase1", "check3") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 1
    assert len(log_warn.msgs) == 0
    assert len(log_error.msgs) == 0

def test_Analysis_analyse_consistency_03():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Multiple requirements used in the matrix do NOT exist
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3", "unknown1", "unknown2"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7", "just1")
    matrix.add_untraceable("unknown3", "just2")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 3
    assert len(log_error.msgs) == 0

def test_Analysis_analyse_consistency_04():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Multiple checks are traced to an untraceable requirement
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3", "req7"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6", "req7"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 1
    assert len(log_error.msgs) == 0

def test_Analysis_analyse_consistency_05():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * One check is traced multiple times to the same requirement
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3", "D_req4", "D_req4", "D_req4"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7", "just1")
    matrix.add_untraceable("req7", "just2")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 2
    assert len(log_error.msgs) == 0

def test_Analysis_analyse_consistency_06():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Untraceable requirements with no justification
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}), \
        Req("req8", "description8", {}), \
        Req("req9", "description9", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7")
    matrix.add_untraceable("req8", "just1")
    matrix.add_untraceable("req9")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 2
    assert len(log_error.msgs) == 0

def test_Analysis_analyse_consistency_07():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Two duplicate requirement ids
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"]}), \
        Req("req6", "description6", {}), \
        Req("req6", "description6", {}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}), \
        Req("req7", "description8", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 0
    assert len(log_error.msgs) == 2

def test_Analysis_analyse_consistency_08():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Two requirement specified in derivedfrom options do NOT exist 
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["unknown1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2", "unknown2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 2
    assert len(log_error.msgs) == 0

def test_Analysis_analyse_consistency_09():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Two requirements have themselves listed as derivedfrom
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["I_req2"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2", "N_req5"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 2
    assert len(log_error.msgs) == 0

def test_Analysis_analyse_consistency_10():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Two duplicate check ids
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2"), \
        Check("testsuite1", "testcase1", "check2"), \
        Check("testsuite1", "testcase1", "check3") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add("testsuite1.testcase1.check3", [])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)

    # A matrix shall be regenerated message is raised here
    assert len(log_imp.msgs) == 1
    assert len(log_warn.msgs) == 0
    assert len(log_error.msgs) == 2

def test_Analysis_analyse_consistency_11():
    """Unit test for the analyse_consistency method of the Analysis class

    The covered behaviors are :
        * Duplicate derivedfrom requirements
    """
    reqs = [ \
        Req("U_req1", "description1", {}), \
        Req("I_req2", "description2", {"derivedfrom": ["U_req1"]}), \
        Req("F_req3", "description3", {}), \
        Req("D_req4", "description4", {"derivedfrom": ["I_req2", "F_req3", "I_req2"]}), \
        Req("N_req5", "description5", {"derivedfrom": ["I_req2", "I_req2", "F_req3", "F_req3", "U_req1"]}), \
        Req("req6", "description6", {}), \
        Req("req7", "description7", {}) \
    ]
    checks = [ \
        Check("testsuite1", "testcase1", "check1"), \
        Check("testsuite1", "testcase1", "check2") \
    ]
    testdata = [ \
        Check("testsuite1", "testcase1", "check1", 0, "msg1"), \
        Check("testsuite1", "testcase1", "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("testsuite1.testcase1.check1", ["F_req3"])
    matrix.add("testsuite1.testcase1.check2", ["D_req4", "req6"])
    matrix.add_untraceable("req7", "just1")

    analysis = Analysis(reqs, checks, testdata, matrix)

    assert len(log_imp.msgs) == 0
    assert len(log_warn.msgs) == 3
    assert len(log_error.msgs) == 0
