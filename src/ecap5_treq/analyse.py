from matrix import check_matrix

class Analysis():
    def __init__(self, reqs, checks, testdata, matrix):
        self.reqs = reqs
        self.checks = checks
        self.testdata = testdata
        self.matrix = matrix

        self.num_successfull_checks = 0
        self.num_failed_checks = 0
        self.testsuites = {}
        self.no_testsuite = []
        self.skipped_checks = []
        self.unknown_checks = []

        self.covered_reqs = []
        self.uncovered_reqs = []
        self.untraceable_reqs = []

        self.is_matrix_too_old = False

        self.test_result = 0

        self.analyse()

    def analyse(self):
        ###################################################
        #                 Tests analysis                  #
        ###################################################

        # Count the number of successfull tests
        self.num_successfull_checks = 0
        for check in self.testdata:
            if check.status == 1:
                self.num_successfull_checks += 1
            else:
                self.num_failed_checks += 1

        # Sort tests in testsuites
        self.testsuites = {}
        self.no_testsuite = []
        for check in self.testdata:
            if check.testsuite:
                if check.testsuite in self.testsuites:
                    self.testsuites[check.testsuite] += [check]
                else:
                    self.testsuites[check.testsuite] = []
            else:
                self.no_testsuite += [check]

        # List skipped checks
        self.skipped_checks = []
        for check in self.checks:
            if check.id not in [c.id for c in self.testdata]:
                self.skipped_checks += [check]

        # List unknown checks
        self.unknown_checks = []
        for check in self.testdata:
            if check.id not in [c.id for c in self.checks]:
                self.unknown_checks += [check]

        # Compute the test result
        self.test_result = int(self.num_successfull_checks / len(self.checks) * 100.0)
        self.traceability_result = 0

        ###################################################
        #              Traceability analysis              #
        ###################################################

        # Checks which requirements are covered by sub-requirements
        self.reqs_covered_by_reqs = {}
        for r in self.reqs:
            if r.derivedFrom:
                if r.derivedFrom not in self.reqs_covered_by_reqs:
                    self.reqs_covered_by_reqs[r.derivedFrom] = [r]
                else:
                    self.reqs_covered_by_reqs[r.derivedFrom] += [r]

        # Checks which requirements are covered by a test from the matrix
        self.reqs_covered_by_checks = {}
        self.reqs_untraceable = []
        for c in self.matrix:
            for rid in self.matrix[c]:
                if c == "__UNTRACEABLE__":
                    self.reqs_untraceable += [rid]
                else:
                    if rid not in self.reqs_covered_by_checks:
                        self.reqs_covered_by_checks[rid] = [c]
                    else:
                        self.reqs_covered_by_checks[rid] += [c]
        
        # Sorts the requirements 
        self.covered_reqs = []
        self.untraceable_reqs = []
        self.uncovered_reqs = []
        for r in self.reqs:
            if (r.id in self.reqs_covered_by_reqs) or (r.id in self.reqs_covered_by_checks):
                self.covered_reqs += [r]
            elif (r.id in self.reqs_untraceable):
                self.untraceable_reqs += [r]
            else:
                self.uncovered_reqs += [r]

        # Checks if the matrix is up to date
        self.is_matrix_too_old = not check_matrix(self.matrix, self.checks)

        print(self.covered_reqs[0].id)
