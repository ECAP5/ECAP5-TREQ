def analyse_tests(reqs, checks, testdata, matrix):
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

    return (count_success, testsuites, no_testsuite, skipped_tests, unknown_tests, checks)
