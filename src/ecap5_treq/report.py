import sys

def generate_test_report(reqs, checks, testdata, matrix, format):

    # Generate the summary table
    count_success = 0
    for check in testdata:
        if check.status == 1:
            count_success += 1

    skipped_tests = []
    for check in checks:
        if check.id not in [c.id for c in testdata]:
            skipped_tests += [check]

    unknown_tests = []
    for check in testdata:
        if check.id not in [c.id for c in checks]:
            print(check.id, checks)
            unknown_tests += [check]

    def generate_html():
        report = "<h1>Test report</h1>"
        report += "<h2>Summary</h2>"
        report += "<table>"
        report += "<tr><td>Test results</td><td>{}%</td></tr>".format(count_success / len(checks) * 100)
        report += "</table>"

        report += "<h2>Run tests</h2>"
        report += "<table>"
        report += "<thead><tr><th>Test check</th><th>Status</th><th>Log</th></tr></thead>"
        for t in testdata:
            report += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(t.id, t.status, t.errormsg if t.errormsg else "")
        report += "</table>"
        report += "<h2>Skipped tests</h2>"
        report += "<table>"
        for t in skipped_tests:
            report += "<tr><td>{}</td></tr>".format(t.id)
        report += "</table>"
        report += "<h2>Unknown tests</h2>"
        report += "<table>"
        for t in unknown_tests:
            report += "<tr><td>{}</td></tr>".format(t.id)
        report += "</table>"
        return report

    def generate_markdown():
        report = "# Test report\n"
        report += "## Summary\n"
        report += "|   |   |\n|---|---|\n"
        report += "| Test results | {} |\n".format(count_success / len(checks) * 100)
        report += "## Run tests\n"
        report += "| Test check | Status | Log |\n"
        report += "|------------|--------|-----|\n"
        for t in testdata:
            report += "| {} | {} | {} |\n".format(t.id, t.status, t.errormsg if t.errormsg else "")
        report += "## Skipped tests\n"
        report += "|   |   |\n|---|---|\n"
        for t in skipped_tests:
            report += "| {} |\n".format(t.id)
        report += "## Unknown tests\n"
        report += "|   |   |\n|---|---|\n"
        for t in unknown_tests:
            report += "| {} |\n".format(t.id)
        return report

    if format == "html":
        report = generate_html()
    elif format == "markdown":
        report = generate_markdown()
    else:
        print("ERROR: Unknown report format", file=sys.stderr) 
        sys.exit(-1)

    return report
