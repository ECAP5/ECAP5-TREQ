def generate_test_report(reqs, checks, testdata, matrix, output):
    report = ""
    
    report += "<h1>Test report</h1>"

    # Generate the summary table
    report += "<h2>Summary</h2>"
    report += "<table>"
    count_success = 0
    for check in testdata:
        if check.status == "OK":
            count_success += 1
    report += "<tr><td>Test results</td><td>{}%</td></tr>".format(count_success / len(checks) * 100)
    report += "</table>"

    # Generate the run test report table
    report += "<h2>Run tests</h2>"
    report += "<table>"
    report += "<thead><tr><th>Test check</th><th>Status</th><th>Log</th></tr></thead>"
    run_tests = []
    for check in testdata:
        run_tests += [check.id]
        report += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(check.id, check.status, check.errormsg if check.errormsg else "")
    report += "</table>"

    report += "<h2>Skipped tests</h2>"
    report += "<table>"
    all_checks = []
    for check in checks:
        all_checks += [check.id]
        if check.id not in run_tests:
            report += "<tr><td>{}</td></tr>".format(check.id)
    report += "</table>"

    report += "<h2>Unknown tests</h2>"
    report += "<table>"
    for check in testdata:
        if check.id not in all_checks:
            report += "<tr><td>{}</td></tr>".format(check.id)
    report += "</table>"

    with open(output, 'w') as f:
        f.write(report)

def generate_trace_report(reqs, checks, matrix, output):
    report = ""
    
    # Generate the summary table
    report += "<h1>Summary</h1>"

    # Generate the traceability report
    report += "<h1>Traceability report</h1>"
    report += "<table>"
    report += "<thead><tr><th>Requirement</th><th>Covered by</th><th>Tested by</th></tr></thead>"
    for req in reqs:
        report += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(req.id, None, None)
    report += "</table>"

    with open(output, 'w') as f:
        f.write(report)
