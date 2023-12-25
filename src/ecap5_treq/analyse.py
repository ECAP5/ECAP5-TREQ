#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
# This file is part of ECAP5-TREQ <https://github.com/cchaine/ECAP5-TREQ>
# 
# ECAP5-TREQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ECAP5-TREQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ECAP5-TREQ.  If not, see <http://www.gnu.org/licenses/>.

from ecap5_treq.matrix import Matrix 
from ecap5_treq.req import Req, ReqStatus
from ecap5_treq.check import Check
from ecap5_treq.log import log_imp, log_warn, log_error

class Analysis():
    """An Analysis contains data analyzed from a requirements, checks, testdata and the traceability matrix
    """

    def __init__(self, reqs: list[Req], checks: list[Check], testdata: list[Check], matrix: Matrix):
        """Constructor of Analysis

        :param reqs: list of requirements from the specification
        :type reqs: list[Req]

        :param checks: list of checks from the tests
        :type checks: list[Check]

        :param testdata: list of checks from testdata with results
        :type testdata: list[Check]

        :param matrix: traceability matrix
        :type matrix: Matrix
        """
        self.reqs = reqs
        self.checks = checks
        self.testdata = testdata
        self.matrix = matrix

        # Data from the test analysis
        self.testsuites = {}
        self.no_testsuite = []
        self.skipped_checks = []
        self.unknown_checks = []
        self.num_successfull_checks = 0
        self.num_failed_checks = 0
        self.check_status_by_check_id = {}
        self.test_result = 0
        
        # Data from the traceability analysis
        self.num_covered_reqs = 0
        self.num_untraceable_reqs = 0
        self.num_uncovered_reqs = 0
        self.reqs_covering_reqs = {}
        self.checks_covering_reqs = {}
        self.ids_reqs_untraceable = []
        self.user_reqs = []
        self.external_interface_reqs = []
        self.functional_reqs = []
        self.design_reqs = []
        self.non_functional_reqs = []
        self.other_reqs = []
        self.traceability_result = 0

        self.analyse()

    def analyse(self) -> None:
        """Perform the analysis
        """
        self.analyse_tests()
        self.analyse_traceability()
        self.analyse_consistency()

    def analyse_tests(self) -> None:
        """Analyse data from the testdata
        """
        # Count the number of successfull tests
        self.num_successfull_checks = 0
        self.num_failed_checks = 0
        self.check_status_by_check_id = {}
        for check in self.testdata:
            if check.status:
                self.num_successfull_checks += 1
            else:
                self.num_failed_checks += 1
            self.check_status_by_check_id[check.id] = check.status

        # Fill the check status to all checks
        for check in self.checks:
            if check.id in self.check_status_by_check_id:
                check.status = self.check_status_by_check_id[check.id]

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
        if len(self.checks) > 0:
            self.test_result = int(self.num_successfull_checks / len(self.checks) * 100.0)
        else:
            self.test_result = 0

    def analyse_traceability(self) -> None:
        """Analyse data from the requirements
        """
        # Checks which requirements are covered by sub-requirements
        self.reqs_covering_reqs = {}
        for req in self.reqs:
            if req.derived_from:
                if req.derived_from not in self.reqs_covering_reqs:
                    self.reqs_covering_reqs[req.derived_from] = [req]
                else:
                    self.reqs_covering_reqs[req.derived_from] += [req]

        # Checks which requirements are covered by a test from the matrix
        self.checks_covering_reqs = {}
        for check in self.checks:
            if check.id in self.matrix:
                for rid in self.matrix.get(check.id):
                    if rid not in self.checks_covering_reqs:
                        self.checks_covering_reqs[rid] = [check]
                    else:
                        self.checks_covering_reqs[rid] += [check]
        # Recover untraceable requirements
        self.ids_reqs_untraceable = []
        for rid in self.matrix.get("__UNTRACEABLE__"):
            self.ids_reqs_untraceable += [rid]
        
        # Set the requirement flags
        self.num_covered_reqs = 0
        self.num_untraceable_reqs = 0
        self.num_uncovered_reqs = 0
        for req in self.reqs:
            if (req.id in self.reqs_covering_reqs) or (req.id in self.checks_covering_reqs):
                req.status = ReqStatus.COVERED
                self.num_covered_reqs += 1
            elif req.id in self.ids_reqs_untraceable:
                req.status = ReqStatus.UNTRACEABLE
                self.num_untraceable_reqs += 1
            else:
                req.status = ReqStatus.UNCOVERED
                self.num_uncovered_reqs += 1

        # Compute the requirement test result
        for req in self.reqs:
            if req.id in self.checks_covering_reqs:
                checks = self.checks_covering_reqs[req.id]
                # Count the number of coverings checks
                req.result = 0
                for check in checks:
                    if check.status:
                        req.result += 1
                # Compute a pourcentage
                req.result = req.result / len(checks) * 100.0

        # Sort requirements based on type
        self.user_reqs = []
        self.external_interface_reqs = []
        self.functional_reqs = []
        self.design_reqs = []
        self.non_functional_reqs = []
        self.other_reqs = []
        for req in self.reqs:
            prefix = req.id.split("_")[0]
            if prefix == "U":
                self.user_reqs += [req]
            elif prefix == "I":
                self.external_interface_reqs += [req]
            elif prefix == "F":
                self.functional_reqs += [req]
            elif prefix == "D":
                self.design_reqs += [req]
            elif prefix == "N":
                self.non_functional_reqs += [req]
            else:
                self.other_reqs += [req]

        # Compute traceability result
        if len(self.reqs) > 0:
            self.traceability_result = int((self.num_covered_reqs + self.num_untraceable_reqs) / len(self.reqs) * 100)
        else:
            self.traceability_result = 0

    def analyse_consistency(self) -> None:
        """Analyse the consistency of the test and traceability data
        """
        # List req ids
        reqs_ids = []
        for req in self.reqs:
            reqs_ids += [req.id]

        ###################################################
        #              Check matrix                       #
        ###################################################

        # Checks if the matrix is up to date
        if not self.matrix.check(self.checks):
            log_imp("The traceability matrix is not up to date and shall be regenerated")

        # Checks if checks are traced to untraceable requirements
        for rid in self.ids_reqs_untraceable:
            if rid in self.checks_covering_reqs:
                log_warn("Requirement \"{}\" is marked untraceable but it is traced to the following tests: {}"\
                            .format(rid, ", ".join([c.id for c in self.checks_covering_reqs[rid]])))

        # Check if requirements used in the matrix exist
        for cid in self.matrix.data:
            for rid in self.matrix.get(cid):
                if rid not in reqs_ids:
                    if cid == "__UNTRACEABLE__":
                        log_warn("Missing requirement \"{}\" marked untraceable in the matrix".format(rid))
                    else:
                        log_warn("Missing requirement \"{}\" traced to check \"{}\" in the matrix".format(rid, cid))

        # Check if the same requirement is traced multiple times to the same check
        for cid in self.matrix.data:
            reqs_ids_seen = set()
            duplicate_reqs = [x for x in self.matrix.get(cid) if x in reqs_ids_seen or reqs_ids_seen.add(x)]  
            if len(duplicate_reqs) > 0:
                for rid in duplicate_reqs:
                    if cid == "__UNTRACEABLE__":
                        log_warn("Requirement \"{}\" is marked untraceable multiple times".format(rid))
                    else:
                        log_warn("Requirement \"{}\" is traced multiple times to the same test \"{}\"".format(rid, cid))

        ###################################################
        #              Check reqs                         #
        ###################################################

        # Checks if there are any duplicate requirement ids
        reqs_ids_seen = set()
        duplicate_reqs = [x for x in reqs_ids if x in reqs_ids_seen or reqs_ids_seen.add(x)]  
        for rid in duplicate_reqs:
            log_error("Multiple requirements share the same id \"{}\"".format(rid))

        # Checks if derivedfrom requirements exist
        for req in self.reqs:
            if req.derived_from:
                if req.derived_from not in reqs_ids:
                    log_warn("Requirement \"{}\" is derived from missing requirement \"{}\""\
                                .format(req.id, req.derived_from))

        # Checks if derivedfrom is different than current
        for req in self.reqs:
            if req.derived_from:
                if req.derived_from == req.id:
                    log_warn("Requirement \"{}\" is derived from itself".format(req.id))

        ###################################################
        #              Check checks                       #
        ###################################################

        # Checks if there are any duplicate check ids
        checks_ids = []
        for check in self.checks:
            checks_ids += [check.id]
        checks_ids_seen = set()
        duplicate_checks = [x for x in checks_ids if x in checks_ids_seen or checks_ids_seen.add(x)]  
        for cid in duplicate_checks:
            log_error("Multiple tests share the same id \"{}\"".format(cid))
