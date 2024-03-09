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

# pylint: disable=line-too-long

import re
import colorsys

from ecap5_treq.analysis import Analysis 
from ecap5_treq.req import Req, ReqStatus
from ecap5_treq.log import log_error, log_imp, log_warn

def generate_report_warning_section() -> str:
    """Generates a string containing messages logged in this tool during the report generation

    :returns: a string containing messages logged in this tool during the report generation
    :rtype: str
    """
    report = ""
    for msg in log_error.msgs:
        report += "\n> [!CAUTION]\n"
        report += "> <samp>{}</samp>\n".format(msg)
    for msg in log_imp.msgs:
        report += "\n> [!IMPORTANT]\n"
        report += "> <samp>{}</samp>\n".format(msg)
    for msg in log_warn.msgs:
        report += "\n> [!WARNING]\n"
        report += "> <samp>{}</samp>\n".format(msg)
    return report

def generate_report_summary(analysis: Analysis) -> str:
    """Generates a string containing the summary section of the report

    :param analysis: the analysis from which data shall be used
    :type analysis: Analysis

    :returns: a string containing the summary section of the report
    :rtype: str
    """
    report = "# Summary\n"

    test_result_icon = "✅" if analysis.test_result == 100 else "🚫"
    traceability_result_icon = "✅" if analysis.traceability_result == 100 else "🚫"
    report += "<table>\n"
    report += "  <tr>\n"
    report += "    <td>{}</td>\n".format(test_result_icon)
    report += "    <td>\n"
    report += "      <a href=\"#test-report\">Test report</a>\n"
    report += "    </td>\n"
    report += "    <td align=\"right\">{}</td>\n".format(str(analysis.test_result) + "%")
    report += "  </tr>\n"
    report += "  <tr>\n"
    report += "    <td>{}</td>\n".format(traceability_result_icon)
    report += "    <td>\n"
    report += "      <a href=\"#traceability-report\">Traceability report</a>\n"
    report += "    </td>\n"
    report += "    <td align=\"right\">{}</td>\n".format(str(analysis.traceability_result) + "%")
    report += "  </tr>\n"
    report += "</table>\n"

    return report

def generate_test_report(analysis: Analysis) -> str:
    """Generates a string containing the test section of the report

    :param analysis: the analysis from which data shall be used
    :type analysis: Analysis

    :returns: a string containing the test section of the report
    :rtype: str
    """
    report = "\n## <a id=\"test-report\"></a> Test report\n"
    report += "<table>\n"
    report += "  <thead>\n"
    report += "    <tr>\n"
    report += "      <th></th>\n"
    report += "      <th>Success</th>\n"
    report += "      <th>Failure</th>\n"
    report += "      <th>Skipped</th>\n"
    report += "      <th>Unknown</th>\n"
    report += "      <th>Total</th>\n"
    report += "    </tr>\n"
    report += "  </thead>\n"
    report += "  <tr>\n"
    report += "    <td>Tests</td>\n"
    report += "    <td align=\"right\">{}</td>\n".format(analysis.num_successfull_checks)
    report += "    <td align=\"right\">{}</td>\n".format(surround_with_link_if(analysis.num_failed_checks > 0, "#first-failed-check", str(analysis.num_failed_checks)))
    report += "    <td align=\"right\">{}</td>\n".format(surround_with_link_if(len(analysis.skipped_checks) > 0, "#skipped-checks", str(len(analysis.skipped_checks))))
    report += "    <td align=\"right\">{}</td>\n".format(surround_with_link_if(len(analysis.unknown_checks) > 0, "#unknown-checks", str(len(analysis.unknown_checks))))
    report += "    <td align=\"right\">{}</td>\n".format(len(analysis.checks))
    report += "  </tr>\n"
    report += "</table>\n"

    report += "\n### Run tests\n\n"
    report += "<table>\n"
    report += "  <thead>\n"
    report += "    <tr>\n"
    report += "      <th>Testsuite</th>\n"
    report += "      <th>Testcase</th>\n"
    report += "      <th>Check ID</th>\n"
    report += "      <th>Status</th>\n"
    report += "      <th>Log</th>\n"
    report += "    </tr>\n"
    report += "  </thead>\n"

    # Checks table
    failed_test_anchor_placed = False
    for testsuite in analysis.testsuites:
        for i, testcase in enumerate(analysis.testsuites[testsuite]):
            for j, check in enumerate(analysis.testsuites[testsuite][testcase]):
                check_status_icon = "✅" if check.status else "🚫"
                report += "  <tr>\n"
                # Insert the name of the testsuite on the first row of each test suite
                if i == 0 and j == 0:
                    report += "    <td rowspan=\"{}\">\n".format(analysis.num_checks_in_testsuites[testsuite])
                    report += "      <samp>{}</samp>\n".format(testsuite)
                    report += "    </td>\n"
                # Insert the name of the testcase on the first row of each testcase
                if j == 0:
                    report += "    <td rowspan=\"{}\">\n".format(len(analysis.testsuites[testsuite][testcase]))
                    report += "      <samp>{}</samp>\n".format(testcase)
                    report += "    </td>\n"
                report += "    <td>\n"
                report += "      <samp>{}</samp>\n".format(check.id)
                report += "    </td>\n"
                report += "    <td align=\"center\">\n"
                # Insert a specific anchor on the first failed check to easily jump to it
                if not check.status and not failed_test_anchor_placed:
                    report += "      <a id=\"first-failed-check\"></a>"
                    failed_test_anchor_placed = True
                report += "      {}\n".format(check_status_icon)
                report += "    </td>\n"
                report += "    <td>{}</td>\n".format(check.error_msg if check.error_msg else "")
                report += "  </tr>\n"
    report += "</table>\n"

    # Handle skipped checks if any
    if len(analysis.skipped_checks) > 0:
        report += "\n### <a id=\"skipped-checks\"></a> Skipped tests\n\n"
        report += "<table>\n"
        for check in analysis.skipped_checks:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(check.id)
            report += "    </td>\n"
            report += "  </tr>\n"
        report += "</table>\n"

    # Handle unknown checks if any
    if len(analysis.unknown_checks) > 0:
        report += "\n### <a id=\"unknown-checks\"></a> Unknown tests\n"
        report += "<table>\n"
        for check in analysis.unknown_checks:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(check.id)
            report += "    </td>\n"
            report += "  </tr>\n"
        report += "</table>\n"

    return report

def generate_traceability_report(analysis: Analysis) -> str:
    """Generates a string containing the traceability section of the report

    :param analysis: the analysis from which data shall be used
    :type analysis: Analysis

    :returns: a string containing the traceability section of the report
    :rtype: str
    """
    report = "\n## <a id=\"traceability-report\"></a> Traceability report\n"
    report += "<table>\n"
    report += "  <thead>\n"
    report += "    <tr>\n"
    report += "      <th></th>\n"
    report += "      <th>Covered</th>\n"
    report += "      <th>Untraceable</th>\n"
    report += "      <th>Uncovered</th>\n"
    report += "      <th>Total</th>\n"
    report += "    </tr>\n"
    report += "  </thead>\n"
    report += "  <tr>\n"
    report += "    <td>Requirements</td>\n"
    report += "    <td align=\"right\">{}</td>\n".format(analysis.num_covered_reqs)
    report += "    <td align=\"right\">{}</td>\n".format(surround_with_link_if(analysis.num_untraceable_reqs > 0, "#untraceable-reqs", str(analysis.num_untraceable_reqs)))
    report += "    <td align=\"right\">{}</td>\n".format(surround_with_link_if(analysis.num_uncovered_reqs > 0, "#uncovered-reqs", str(analysis.num_uncovered_reqs)))
    report += "    <td align=\"right\">{}</td>\n".format(len(analysis.reqs))
    report += "  </tr>\n"
    report += "</table>\n"

    # Handle covered requirements if any
    if analysis.num_covered_reqs > 0:
        # Get lists of covered requirements based on their type
        filtered_user_reqs               = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.user_reqs))
        filtered_external_interface_reqs = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.external_interface_reqs))
        filtered_functional_reqs         = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.functional_reqs))
        filtered_architecture_reqs       = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.architecture_reqs))
        filtered_design_reqs             = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.design_reqs))
        filtered_non_functional_reqs     = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.non_functional_reqs))
        filtered_other_reqs              = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.other_reqs))

        report += "\n### Covered requirements\n"
        report += "<table>\n"
        report += "  <thead>\n"
        report += "    <tr>\n"
        report += "      <th>Requirement</th>\n"
        report += "      <th>Description</th>\n"
        report += "      <th>Covered by</th>\n"
        report += "      <th>Tested by</th>\n"
        report += "      <th>Test results</th>\n"
        report += "    </tr>\n"
        report += "  </thead>\n"
        # Add rows for each type of covered requirements
        if len(filtered_user_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>User Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_user_reqs)
        if len(filtered_external_interface_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>External Interface Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_external_interface_reqs)
        if len(filtered_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_functional_reqs)
        if len(filtered_architecture_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>Architecture Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_architecture_reqs)
        if len(filtered_design_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>Design Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_design_reqs)
        if len(filtered_non_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>Non-Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_non_functional_reqs)
        if len(filtered_other_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>Other Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_other_reqs)
        report += "</table>\n"

    # Handle untraceable requirements if any
    if analysis.num_untraceable_reqs > 0:
        # Get lists of untraceable requirements based on their type
        filtered_user_reqs               = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.user_reqs))
        filtered_external_interface_reqs = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.external_interface_reqs))
        filtered_functional_reqs         = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.functional_reqs))
        filtered_architecture_reqs       = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.architecture_reqs))
        filtered_design_reqs             = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.design_reqs))
        filtered_non_functional_reqs     = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.non_functional_reqs))
        filtered_other_reqs              = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.other_reqs))

        report += "\n### <a id=\"untraceable-reqs\"></a> Untraceable requirements\n"
        report += "<table>\n"
        report += "  <thead>\n"
        report += "    <tr>\n"
        report += "      <th>Requirement</th>\n"
        report += "      <th>Description</th>\n"
        report += "    </tr>\n"
        report += "  </thead>\n"
        # Add rows for each type of untraceable requirements
        if len(filtered_user_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>User Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_user_reqs)
        if len(filtered_external_interface_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>External Interface Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_external_interface_reqs)
        if len(filtered_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_functional_reqs)
        if len(filtered_architecture_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Architecture Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_architecture_reqs)
        if len(filtered_design_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Design Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_design_reqs)
        if len(filtered_non_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Non-Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_non_functional_reqs)
        if len(filtered_other_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Other Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_other_reqs)
        report += "</table>\n"

    # Handle untraceable requirements if any
    if analysis.num_uncovered_reqs > 0:
        # Get lists of uncovered requirements based on their type
        filtered_user_reqs               = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.user_reqs))
        filtered_external_interface_reqs = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.external_interface_reqs))
        filtered_functional_reqs         = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.functional_reqs))
        filtered_architecture_reqs       = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.architecture_reqs))
        filtered_design_reqs             = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.design_reqs))
        filtered_non_functional_reqs     = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.non_functional_reqs))
        filtered_other_reqs              = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.other_reqs))

        report += "\n### <a id=\"uncovered-reqs\"></a> Uncovered requirements\n"
        report += "<table>\n"
        report += "  <thead>\n"
        report += "    <tr>\n"
        report += "      <th>Requirement</th>\n"
        report += "      <th>Description</th>\n"
        report += "    </tr>\n"
        report += "  </thead>\n"
        # Add rows for each type of uncovered requirements
        if len(filtered_user_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>User Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_user_reqs)
        if len(filtered_external_interface_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>External Interface Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_external_interface_reqs)
        if len(filtered_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_functional_reqs)
        if len(filtered_architecture_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Architecture Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_architecture_reqs)
        if len(filtered_design_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Design Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_design_reqs)
        if len(filtered_non_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Non-Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_non_functional_reqs)
        if len(filtered_other_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Other Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_other_reqs)
        report += "</table>\n"

    return report

def generate_test_result_badge(analysis: Analysis) -> str:
    """Generate badge data indicating the test result, which color changes on the result

    :param analysis: the analysis from which data shall be used
    :type analysis: Analysis

    :returns: a json string containing the badge data
    :rtype: str
    """ 
    badge = "{"
    badge += "\"schemaVersion\": 1, "
    badge += "\"label\": \"Test result\", "
    badge += "\"message\": \"{}%\", ".format(analysis.test_result)
    badge += "\"color\": \"hsl({}, 100%, 40%)\"".format(analysis.test_result)
    badge += "}"
    return badge

def generate_traceability_result_badge(analysis: Analysis) -> str:
    """Generate badge data indicating the traceability result, which color changes on the result

    :param analysis: the analysis from which data shall be used
    :type analysis: Analysis

    :returns: a json string containing the badge data
    :rtype: str
    """ 
    badge = "{"
    badge += "\"schemaVersion\": 1, "
    badge += "\"label\": \"Traceability\", "
    badge += "\"message\": \"{}%\", ".format(analysis.traceability_result)
    badge += "\"color\": \"hsl({}, 100%, 40%)\"".format(analysis.traceability_result)
    badge += "}"
    return badge

def surround_with_link_if(cond: bool, href: str, content: str) -> str:
    """Returns the content string surrounded by a link to href if cond is true

    :param cond: condition boolean indicating if the content shall be surrounded
    :type cond: bool

    :param href: path used for the link
    :type href: str

    :param content: the content to be surrounded
    :type content: str

    :returns: the content string surrounded by a link to href if cond is true
    :rtype: str
    """
    res = None
    if cond:
        res = "<a href=\"{}\">{}</a>".format(href, content)
    else:
        res = content
    return res

def latex_to_html(content: str) -> str:
    """Converts a latex string to html formating

    :param content: the latex string to convert
    :type content: str

    :returns: the content string converted to html formatting
    :rtype: str
    """
    if content is None:
        return None

    result = content 
    # Replace \texttt{} with samp
    result = re.sub(r"\\texttt{([^}]*)}", r"<samp>\1</samp>", result)
    # Replace \_ with _
    result = re.sub(r"\\_", "_", result)
    # Replace \textsuperscript with sup
    result = re.sub(r"\\textsuperscript{([^}]*)}", r"<sup>\1</sup>", result)

    return result

def gen_result_badge(result: float) -> str:
    """Generates a badge containing the result pourcentage, which color is dependant on the result

    :param result: the result to be included in the badge
    :type result: float

    :returns: a badge containing the result pourcentage, which color is dependant on the result
    :rtype: str
    """
    rgb_color = colorsys.hsv_to_rgb(int(result) / 360.0, 1.0, 0.8)
    hex_color = '{:02x}{:02x}{:02x}'.format(*tuple(int(255*i) for i in rgb_color))
    badge = "<img src=\"https://img.shields.io/badge/{}%25-{}\"/>".format(int(result), hex_color)
    return badge

def req_list_to_table_rows(analysis: Analysis, reqs: list[Req]) -> str:
    """Converts a list of reqs into html table rows

    :param analysis: the analysis from which data shall be used
    :type analysis: Analysis

    :param reqs: the list of reqs to convert
    :type reqs: list[Req]

    :returns: html table rows containing the list of reqs
    :rtype: str
    """
    result = ""
    for req in reqs:
        result += "  <tr>\n"
        result += "    <td valign=\"top\">\n"
        result += "      <samp><b>{}</b></samp>\n".format(req.id)
        result += "    </td>\n"
        result += "    <td valign=\"top\">{}</td>\n".format(latex_to_html(req.description))
        if req.status == ReqStatus.COVERED:
            # Adds the list of covering reqs
            if req.id in analysis.ids_reqs_covering_reqs:
                result += "    <td valign=\"top\"><samp>{}</samp></td>\n".format("<br>".join([rid for rid in analysis.ids_reqs_covering_reqs[req.id]]))
            else:
                result += "    <td></td>\n"
            # Adds the list of covering checks
            if req.id in analysis.ids_checks_covering_reqs:
                result += "    <td valign=\"top\"><samp>{}</samp></td>\n".format("<br>".join([cid for cid in analysis.ids_checks_covering_reqs[req.id]]))
                result += "    <td valign=\"top\" align=\"center\">\n"
                result += "      {}\n".format(gen_result_badge(req.result))
                result += "    </td>\n"
            else:
                result += "    <td></td>\n"
                result += "    <td></td>\n"
        result += "  </tr>\n"
    return result
