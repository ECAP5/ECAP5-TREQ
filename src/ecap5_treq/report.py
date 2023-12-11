import sys
import os

def generate_test_report(reqs, checks, testdata, matrix, format):
    return ""

def generate_test_summary(count_success, testsuites, no_testsuite, skipped_tests, unknown_tests, checks):
    report = "# Test report\n"
    report += "<table>\n"
    report += "<thead><tr><th>Success</th><th>Failure</th><th>Total</th></tr></thead>\n"
    report += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>\n".format(count_success, len(checks)-count_success, len(checks))
    report += "</table>\n\n"

    report += "## Run tests\n"
    report += "<table>\n"
    report += "<thead><tr><th>Testsuite</th><th>Test check</th><th>Status</th><th>Log</th></tr></thead>\n"
    for t in testsuites:
        for i, c in enumerate(testsuites[t]):
            report += "<tr>"
            if i == 0:
                report += "<td rowspan=\"{}\"><samp>{}</samp></td>".format(len(testsuites[t]), t)
            report += "<td><samp>{}</samp></td><td>{}</td><td>{}</td></tr>\n".format(c.id, "✅" if c.status else "🚫", c.errormsg if c.errormsg else "")
    # Handle tests that do not belong to a testsuite
    for i, c in enumerate(no_testsuite):
        report += "<tr>"
        if i == 0:
            report += "<td rowspan=\"{}\"></td>".format(len(no_testsuite))
        report += "<td><samp>{}</samp></td><td>{}</td><td>{}</td></tr>\n".format(c.id, "✅" if c.status else "🚫", c.errormsg if c.errormsg else "")
    report += "</table>\n\n"

    if(len(skipped_tests) > 0):
        report += "## Skipped tests\n"
        report += "<table>\n"
        for t in skipped_tests:
            report += "<tr><td><samp>{}</samp></td></tr>\n".format(t.id)
        report += "</table>\n\n"

    if(len(unknown_tests) > 0):
        report += "## Unknown tests\n"
        report += "<table>\n"
        for t in unknown_tests:
            report += "<tr><td><samp>{}</samp></td></tr>\n".format(t.id)
        report += "</table>\n\n"

    return report

def generate_test_result_badge(count_success, checks):
    badge = "{"
    badge += "\"schemaVersion\": 1, "
    badge += "\"label\": \"Test result\", "
    badge += "\"message\": \"{}%\", ".format(str(count_success / len(checks) * 100))
    badge += "\"color\": \"hsl({}, 60%, 50%)\"".format(str(int(count_success / len(checks) * 100.0)))
    badge += "}"
    return badge
