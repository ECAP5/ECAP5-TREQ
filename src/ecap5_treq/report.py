import sys
import os

def surround_with_link_if(cond, href, content):
    res = ""
    if cond:
        res = "<a href=\"{}\">{}</a>".format(href, content)
    else:
        res = content
    return res

def generate_report_summary(analysis):
    test_result_icon = "✅" if analysis.test_result == 100 else "🚫"
    traceability_result_icon = "✅" if analysis.traceability_result == 100 else "🚫"

    report = "# Summary\n"

    # Adds warnings
    if analysis.is_matrix_too_old:
        report += "\n> [!CAUTION]\n"
        report += "> The traceability matrix is not up to date and shall be regenerated\n"

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
            report += "      <samp>{}</samp>\n".format(c.id)
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
        report += "      <samp>{}</samp>\n".format(c.id)
        report += "    </td>\n"
        report += "    <td align=\"center\">{}</td>\n".format("✅" if c.status else "🚫")
        report += "    <td>{}</td>\n".format(c.errormsg if c.errormsg else "")
        report += "  </tr>\n"
    report += "</table>\n"

    if(len(analysis.skipped_checks) > 0):
        report += "\n### <a id=\"skipped-checks\"></a> Skipped tests\n"
        report += "<table>\n"
        for t in analysis.skipped_checks:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(t.id)
            report += "    </td>\n"
            report += "  </tr>\n"
        report += "</table>\n"

    if(len(analysis.unknown_checks) > 0):
        report += "\n### <a id=\"unknown-checks\"></a> Unknown tests\n"
        report += "<table>\n"
        for t in analysis.unknown_checks:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(t.id)
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
    report += "    <td align=\"right\">{}</td>\n".format(len(analysis.covered_reqs))
    report += "    <td align=\"right\">{}</td>\n".format(surround_with_link_if(len(analysis.untraceable_reqs) > 0, "#untraceable-reqs", str(len(analysis.untraceable_reqs))))
    report += "    <td align=\"right\">{}</td>\n".format(surround_with_link_if(len(analysis.uncovered_reqs) > 0, "#uncovered-reqs", str(len(analysis.uncovered_reqs))))
    report += "    <td align=\"right\">{}</td>\n".format(len(analysis.reqs))
    report += "  </tr>\n"
    report += "</table>\n"

    if(len(analysis.covered_reqs) > 0):
        report += "\n### Covered requirements\n"
        report += "<table>\n"
        report += "  <thead>\n"
        report += "    <tr>\n"
        report += "      <th></th>\n"
        report += "      <th>Covered by</th>\n"
        report += "      <th>Tested by</th>\n"
        report += "    </tr>\n"
        report += "  </thead>\n"
        for r in analysis.covered_reqs:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(r.id)
            report += "    </td>\n"
            # Adds the list of covering reqs
            if r.id in analysis.reqs_covered_by_reqs:
                report += "    <td><samp>{}</samp></td>\n".format("<br>".join([e.id for e in analysis.reqs_covered_by_reqs[r.id]]))
            else:
                report += "    <td></td>\n"
            # Adds the list of covering checks
            if r.id in analysis.reqs_covered_by_checks:
                report += "    <td><samp>{}</samp></td>\n".format("<br>".join(analysis.reqs_covered_by_checks[r.id]))
            else:
                report += "    <td></td>\n"
            report += "  </tr>\n"
        report += "</table>\n"

    if(len(analysis.untraceable_reqs) > 0):
        report += "\n### <a id=\"untraceable-reqs\"></a> Untraceable requirements\n"
        report += "<table>\n"
        for r in analysis.untraceable_reqs:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(r.id)
            report += "    </td>\n"
            report += "  </tr>\n"
        report += "</table>\n"

    if(len(analysis.uncovered_reqs) > 0):
        report += "\n### <a id=\"uncovered-reqs\"></a> Uncovered requirements\n"
        report += "<table>\n"
        for r in analysis.uncovered_reqs:
            report += "  <tr>\n"
            report += "    <td>\n"
            report += "      <samp>{}</samp>\n".format(r.id)
            report += "    </td>\n"
            report += "  </tr>\n"
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
