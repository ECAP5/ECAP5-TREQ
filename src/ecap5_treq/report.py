import sys
import os
import re
from req import ReqStatus

def surround_with_link_if(cond, href, content):
    res = ""
    if cond:
        res = "<a href=\"{}\">{}</a>".format(href, content)
    else:
        res = content
    return res

def latex_to_html(text):
    if text == None:
        return None

    result = text
    # Replace \texttt{} with samp
    result = re.sub(r"\\texttt{([^}]*)}", r"<samp>\1</samp>", result)
    # Replace \_ with _
    result = re.sub(r"\\_", "_", result)
    # Replace \textsuperscript with sup
    result = re.sub(r"\\textsuperscript{([^}]*)}", r"<sup>\1</sup>", result)

    return result

def req_list_to_table_rows(analysis, reqs):
    result = ""
    for r in reqs:
        result += "  <tr>\n"
        result += "    <td valign=\"top\">\n"
        result += "      <samp><b>{}</b></samp>\n".format(r.id)
        result += "    </td>\n"
        result += "    <td valign=\"top\">{}</td>\n".format(latex_to_html(r.description))
        if r.status == ReqStatus.COVERED:
            # Adds the list of covering reqs
            if r.id in analysis.reqs_covered_by_reqs:
                result += "    <td valign=\"top\"><samp>{}</samp></td>\n".format("<br>".join([e.id for e in analysis.reqs_covered_by_reqs[r.id]]))
            else:
                result += "    <td></td>\n"
            # Adds the list of covering checks
            if r.id in analysis.reqs_covered_by_checks:
                result += "    <td valign=\"top\"><samp>{}</samp></td>\n".format("<br>".join(analysis.reqs_covered_by_checks[r.id]))
            else:
                result += "    <td></td>\n"
            result += "    <td></td>\n"
        result += "  </tr>\n"
    return result

def generate_report_summary(analysis):
    print(latex_to_html("this is a text and \\texttt{this shall be surrounded} and this shall not"))
    report = ""

    # Adds warnings
    if analysis.is_matrix_too_old:
        report += "\n> [!CAUTION]\n"
        report += "> The traceability matrix is not up to date and shall be regenerated\n"

    report += "# Summary\n"

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

def generate_test_report(analysis):
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

    report += "\n### Run tests\n"
    report += "<table>\n"
    report += "  <thead>\n"
    report += "    <tr>\n"
    report += "      <th>Testsuite</th>\n"
    report += "      <th>Test check</th>\n"
    report += "      <th>Status</th>\n"
    report += "      <th>Log</th>\n"
    report += "    </tr>\n"
    report += "  </thead>\n"
    failed_test_anchor_placed = False
    for t in analysis.testsuites:
        for i, c in enumerate(analysis.testsuites[t]):
            check_status_icon = "✅" if c.status else "🚫"
            report += "  <tr>\n"
            # Insert the name of the testsuite on the first row
            if i == 0:
                report += "    <td rowspan=\"{}\">\n".format(len(analysis.testsuites[t]))
                report += "      <samp>{}</samp>\n".format(t)
                report += "    </td>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(c.shortid)
            report += "    </td>\n"
            report += "    <td align=\"center\">\n"
            if not c.status and not failed_test_anchor_placed:
                report += "      <a id=\"first-failed-check\"></a>"
                failed_test_anchor_placed = True
            report += "      {}\n".format(check_status_icon)
            report += "    </td>\n"
            report += "    <td>{}</td>\n".format(c.errormsg if c.errormsg else "")
            report += "  </tr>\n"

    # Handle tests that do not belong to a testsuite
    for i, c in enumerate(analysis.no_testsuite):
        report += "  <tr>\n"
        # Insert the name of the testsuite on the first row
        if i == 0:
            report += "    <td rowspan=\"{}\"></td>\n".format(len(analysis.no_testsuite))
        report += "    <td>\n"
        report += "      <samp>{}</samp>\n".format(c.shortid)
        report += "    </td>\n"
        report += "    <td align=\"center\">{}</td>\n".format("✅" if c.status else "🚫")
        report += "    <td>{}</td>\n".format(c.errormsg if c.errormsg else "")
        report += "  </tr>\n"
    report += "</table>\n"

    if(len(analysis.skipped_checks) > 0):
        report += "\n### <a id=\"skipped-checks\"></a> Skipped tests\n"
        report += "<table>\n"
        for c in analysis.skipped_checks:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(c.shortid)
            report += "    </td>\n"
            report += "  </tr>\n"
        report += "</table>\n"

    if(len(analysis.unknown_checks) > 0):
        report += "\n### <a id=\"unknown-checks\"></a> Unknown tests\n"
        report += "<table>\n"
        for c in analysis.unknown_checks:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(c.shortid)
            report += "    </td>\n"
            report += "  </tr>\n"
        report += "</table>\n"

    return report

def generate_traceability_report(analysis):
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

    if(analysis.num_covered_reqs > 0):
        filtered_user_reqs               = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.user_reqs))
        filtered_external_interface_reqs = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.external_interface_reqs))
        filtered_functional_reqs         = list(filter(lambda r: r.status == ReqStatus.COVERED, analysis.functional_reqs))
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
        if len(filtered_user_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>User Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_user_reqs)
        if len(filtered_external_interface_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>External Interface Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_external_interface_reqs)
        if len(filtered_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"5\"><i>Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_functional_reqs)
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

    if(analysis.num_untraceable_reqs > 0):
        filtered_user_reqs               = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.user_reqs))
        filtered_external_interface_reqs = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.external_interface_reqs))
        filtered_functional_reqs         = list(filter(lambda r: r.status == ReqStatus.UNTRACEABLE, analysis.functional_reqs))
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
        if len(filtered_user_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>User Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_user_reqs)
        if len(filtered_external_interface_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>External Interface Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_external_interface_reqs)
        if len(filtered_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_functional_reqs)
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

    if(analysis.num_uncovered_reqs > 0):
        filtered_user_reqs               = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.user_reqs))
        filtered_external_interface_reqs = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.external_interface_reqs))
        filtered_functional_reqs         = list(filter(lambda r: r.status == ReqStatus.UNCOVERED, analysis.functional_reqs))
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
        if len(filtered_user_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>User Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_user_reqs)
        if len(filtered_external_interface_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>External Interface Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_external_interface_reqs)
        if len(filtered_functional_reqs) > 0:
            report += "  <thead><tr><th colspan=\"2\"><i>Functional Requirements</i></th></tr></thead>\n"
            report += req_list_to_table_rows(analysis, filtered_functional_reqs)
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

def generate_test_result_badge(analysis):
    badge = "{"
    badge += "\"schemaVersion\": 1, "
    badge += "\"label\": \"Test result\", "
    badge += "\"message\": \"{}%\", ".format(str(analysis.test_result) + "%")
    badge += "\"color\": \"hsl({}, 60%, 50%)\"".format(str(analysis.test_result))
    badge += "}"
    return badge
