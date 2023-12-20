from matrix import check_matrix
from req import ReqStatus

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
        
        self.num_covered_reqs = 0
        self.num_untraceable_reqs = 0
        self.num_uncovered_reqs = 0

        self.is_matrix_too_old = False

        self.test_result = 0

        self.analyse()

    def analyse(self):
        ###################################################
        #                 Tests analysis                  #
        ###################################################

        # Count the number of successfull tests
        self.num_successfull_checks = 0
        self.check_status_by_check_id = {}
        for check in self.testdata:
            if check.status == 1:
                self.num_successfull_checks += 1
            else:
                self.num_failed_checks += 1
            self.check_status_by_check_id[check.id] = check.status

        # Fill the check status to all checks
        for c in self.checks:
            if c.id in self.check_status_by_check_id:
                c.status = self.check_status_by_check_id[c.id]

        # Sort tests in testsuites
        self.testsuites = {}
        self.no_testsuite = []
        for check in self.testdata:
            if check.testsuite:
                if check.testsuite in self.testsuites:
                    self.testsuites[check.testsuite] += [check]
                else:
                    self.testsuites[check.testsuite] = [check]
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
        self.reqs_covering_reqs = {}
        for r in self.reqs:
            if r.derivedFrom:
                if r.derivedFrom not in self.reqs_covering_reqs:
                    self.reqs_covering_reqs[r.derivedFrom] = [r]
                else:
                    self.reqs_covering_reqs[r.derivedFrom] += [r]

        # Checks which requirements are covered by a test from the matrix
        self.checks_covering_reqs = {}
        for c in self.checks:
            if c.id in self.matrix:
                matrix_entry = self.matrix[c.id]
                for rid in matrix_entry:
                    if rid not in self.checks_covering_reqs:
                        self.checks_covering_reqs[rid] = [c]
                    else:
                        self.checks_covering_reqs[rid] += [c]
        # Recover untraceable requirements
        self.ids_reqs_untraceable = []
        if "__UNTRACEABLE__" in self.matrix:
            for rid in self.matrix["__UNTRACEABLE__"]:
                self.ids_reqs_untraceable += [rid]
        
        # Set the requirement flags
        self.num_covered_reqs = 0
        self.num_untraceable_reqs = 0
        self.num_uncovered_reqs = 0
        for r in self.reqs:
            if (r.id in self.reqs_covering_reqs) or (r.id in self.checks_covering_reqs):
                r.status = ReqStatus.COVERED
                self.num_covered_reqs += 1
            elif (r.id in self.ids_reqs_untraceable):
                r.status = ReqStatus.UNTRACEABLE
                self.num_untraceable_reqs += 1
            else:
                r.status = ReqStatus.UNCOVERED
                self.num_uncovered_reqs += 1

        # Compute the requirement test result
        for r in self.reqs:
            if r.id in self.checks_covering_reqs:
                checks = self.checks_covering_reqs[r.id]
                result = 0
                for c in checks:
                    if c.status == 1:
                        result += 1
                result = result / len(checks) * 100.0
                r.result = result

        # Sort requirements based on type
        self.user_reqs = []
        self.external_interface_reqs = []
        self.functional_reqs = []
        self.design_reqs = []
        self.non_functional_reqs = []
        self.other_reqs = []
        for r in self.reqs:
            prefix = r.id.split("_")[0]
            if prefix == "U":
                self.user_reqs += [r]
            elif prefix == "I":
                self.external_interface_reqs += [r]
            elif prefix == "F":
                self.functional_reqs += [r]
            elif prefix == "D":
                self.design_reqs += [r]
            elif prefix == "N":
                self.non_functional_reqs += [r]
            else:
                self.other_reqs += [r]

        # Checks if the matrix is up to date
        self.is_matrix_too_old = not check_matrix(self.matrix, self.checks)
