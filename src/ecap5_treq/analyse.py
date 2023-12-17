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
        self.reqs_derived_from = {}
        for r in self.reqs:
            if r.derivedFrom:
                if r.derivedFrom not in self.reqs_derived_from:
                    self.reqs_derived_from[r.derivedFrom] = [r]
                else:
                    self.reqs_derived_from[r.derivedFrom] += [r]

        # Checks which requirements are covered by a test from the matrix
        self.reqs_covered_by_test = {}
        for c in self.matrix:
           print(self.matrix[c]) 
           for rid in self.matrix[c]:
               if rid not in self.reqs_covered_by_test:
                   self.reqs_covered_by_test[rid] = [c]
               else:
                   self.reqs_covered_by_test[rid] += [c]

        self.covered_reqs = []
        for r in self.reqs:
            if (r.id in self.reqs_derived_from) or (r.id in self.reqs_covered_by_test):
                self.covered_reqs += [r]

        self.uncovered_reqs = []
