def generate_html_report(reqs, checks, matrix, output):
    report = ""
    
    # Generate the summary table
    report += "<h1>Summary</h1>"
    report += "<table>"
    count_success = 0
    for check in checks:
        if check.status == "OK":
            count_success += 1
    report += "<tr><td>Test results</td><td>{}/{}</td></tr>".format(count_success, len(checks))
    report += "</table>"

    # Generate the test report table
    report += "<h1>Test report</h1>"
    report += "<table>"
    report += "<thead><tr><th>Test check</th><th>Status</th><th>Log</th></tr></thead>"
    for check in checks:
        report += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(check.id, check.status, check.errormsg)
    report += "</table>"

    # Generate the traceability report
    report += "<h1>Traceability report</h1>"
    report += "<table>"
    report += "<thead><tr><th>Requirement</th><th>Covered by</th><th>Tested by</th></tr></thead>"
    for req in reqs:
        report += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(req.id, None, None)
    report += "</table>"

    with open(output, 'w') as f:
        f.write(report)
