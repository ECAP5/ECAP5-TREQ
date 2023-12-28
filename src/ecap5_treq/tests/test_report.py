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

from ecap5_treq.req import Req
from ecap5_treq.check import Check
from ecap5_treq.matrix import Matrix 
from ecap5_treq.analyse import Analysis 
from ecap5_treq.report import generate_report_warning_section, generate_report_summary, generate_test_report, generate_traceability_report, generate_test_result_badge, generate_traceability_result_badge, surround_with_link_if, latex_to_html, gen_result_badge, req_list_to_table_rows
from ecap5_treq.log import log_error, log_clear, log_imp, log_warn

#
# Fixture definitions
#

@pytest.fixture(autouse=True)
def reset():
    log_clear()

#
# Tests targetting functions of the report module
#

def test_generate_report_warning_section():
    """Unit test for the generate_report_warning_section function

    The function is run but no checks are performed on the output
    """
    log_error("error1")
    log_error("error2")
    log_error("error3")

    log_imp("imp1")
    log_imp("imp2")

    log_warn("warn1")
    log_warn("warn2")
    log_warn("warn3")
    log_warn("warn4")

    generate_report_warning_section()

def test_generate_report_summary():
    """Unit test for the generate_report_summary function

    The function is run but no checks are performed on the output
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
        Check(None, "check1"), \
        Check(None, "check2") \
    ]
    testdata = [ \
        Check(None, "check1", 0, "msg1"), \
        Check(None, "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("check1", ["F_req3"])
    matrix.add("check2", ["D_req4", "req6"])
    matrix.add("__UNTRACEABLE__", ["req7"])

    analysis = Analysis(reqs, checks, testdata, matrix)

    generate_report_summary(analysis)

def test_generate_test_report():
    """Unit test for the generate_test_report function

    The function is run but no checks are performed on the output
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
        Check(None, "check1"), \
        Check(None, "check2") \
    ]
    testdata = [ \
        Check(None, "check1", 0, "msg1"), \
        Check(None, "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("check1", ["F_req3"])
    matrix.add("check2", ["D_req4", "req6"])
    matrix.add("__UNTRACEABLE__", ["req7"])

    analysis = Analysis(reqs, checks, testdata, matrix)

    generate_test_report(analysis)

def test_generate_traceability_report():
    """Unit test for the generate_traceability_report function

    The function is run but no checks are performed on the output
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
        Check(None, "check1"), \
        Check(None, "check2") \
    ]
    testdata = [ \
        Check(None, "check1", 0, "msg1"), \
        Check(None, "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("check1", ["F_req3"])
    matrix.add("check2", ["D_req4", "req6"])
    matrix.add("__UNTRACEABLE__", ["req7"])

    analysis = Analysis(reqs, checks, testdata, matrix)

    generate_traceability_report(analysis)

def test_generate_test_result_badge():
    """Unit test for the generate_test_result_badge function

    The function is run but no checks are performed on the output
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
        Check(None, "check1"), \
        Check(None, "check2") \
    ]
    testdata = [ \
        Check(None, "check1", 0, "msg1"), \
        Check(None, "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("check1", ["F_req3"])
    matrix.add("check2", ["D_req4", "req6"])
    matrix.add("__UNTRACEABLE__", ["req7"])

    analysis = Analysis(reqs, checks, testdata, matrix)

    generate_test_result_badge(analysis)

def test_generate_traceability_result_badge():
    """Unit test for the generate_traceability_result_badge function

    The function is run but no checks are performed on the output
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
        Check(None, "check1"), \
        Check(None, "check2") \
    ]
    testdata = [ \
        Check(None, "check1", 0, "msg1"), \
        Check(None, "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("check1", ["F_req3"])
    matrix.add("check2", ["D_req4", "req6"])
    matrix.add("__UNTRACEABLE__", ["req7"])

    analysis = Analysis(reqs, checks, testdata, matrix)

    generate_traceability_result_badge(analysis)

def test_surround_with_link_if():
    """Unit test for the surround_with_link_if function

    The covered requirements are:
        * Cond equal True
        * Cond equal False

    The function is run but no checks are performed on the output
    """
    surround_with_link_if(False, "href", "content")
    surround_with_link_if(True, "href", "content")

def test_latex_to_html():
    """Unit test for the latex_to_html function
    """
    assert latex_to_html("content") == "content"
    assert latex_to_html("content \\texttt{val} end") == "content <samp>val</samp> end"
    assert latex_to_html("content ID\\_01") == "content ID_01"
    assert latex_to_html("content 1\\textsuperscript{st} end") == "content 1<sup>st</sup> end"


def test_gen_result_badge():
    """Unit test for the gen_result_badge function

    The function is run but no checks are performed on the output
    """
    gen_result_badge(0)
    gen_result_badge(10)
    gen_result_badge(80)
    gen_result_badge(100)

def test_req_list_to_table_rows():
    """Unit test for the req_list_to_table_rows function

    The function is run but no checks are performed on the output
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
        Check(None, "check1"), \
        Check(None, "check2") \
    ]
    testdata = [ \
        Check(None, "check1", 0, "msg1"), \
        Check(None, "check2", 1, "msg1") \
    ]
    matrix = Matrix()
    matrix.add("check1", ["F_req3"])
    matrix.add("check2", ["D_req4", "req6"])
    matrix.add("__UNTRACEABLE__", ["req7"])

    analysis = Analysis(reqs, checks, testdata, matrix)

    req_list_to_table_rows(analysis, reqs)
