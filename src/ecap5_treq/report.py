def generate_html_report(checks):
    with open("index.html", 'w') as f:
        f.write("<table><thead><tr><th>Test check</th><th>Status</th><th>Covered requirements</th></tr></thead>")
        for check in checks:
            f.write("<tr><td>{}</td><td>{}</td><td>{}</td>".format(check.id, check.status, None))
