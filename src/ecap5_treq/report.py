import sys
import os

def generate_test_report(reqs, checks, testdata, matrix, format):
    return ""

def generate_test_summary(reqs, checks, testdata, matrix, format):
    # Generate the summary table
    count_success = 0
    failing_testsuites = {}
    for check in testdata:
        if check.status == 1:
            count_success += 1
        else:
            if check.testsuite:
                failing_testsuites[check.testsuite] = True

    testsuites = {}
    no_testsuite = []
    for check in testdata:
        if check.testsuite:
            if check.testsuite in testsuites:
                testsuites[check.testsuite] += [check]
            else:
                testsuites[check.testsuite] = []
        else:
            no_testsuite += [check]

    skipped_tests = []
    for check in checks:
        if check.id not in [c.id for c in testdata]:
            skipped_tests += [check]

    unknown_tests = []
    for check in testdata:
        if check.id not in [c.id for c in checks]:
            print(check.id, checks)
            unknown_tests += [check]

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

    # Set environment variables for the status
    os.environ["ECAP5_TREQ_TEST_STATUS"] = count_success / len(checks) * 100

    return report
