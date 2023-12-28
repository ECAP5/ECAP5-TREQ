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

# pylint: disable=redefined-builtin

import re
import sys
import csv
import glob

from ecap5_treq.log import log_warn, log_error

class Check:
    """A Check is a test that can be traced to requirements
    """

    def __init__(self, testsuite: str, id: str, status: int = None, error_msg: str = None):
        """Constructor of Check

        :param testsuite: name of the testsuite to which the check is associated
        :type testsuite: str

        :param id: identifier of the check
        :type id: str

        :param status: true if the check was run successfully
        :type status: int, optional

        :param error_msg: message associated to a failed check
        :type error_msg: str, optional
        """
        self.testsuite = None
        if testsuite:
            self.testsuite = testsuite.strip()
            self.id = testsuite.strip() + "." + id.strip()
        else:
            self.id = id.strip()

        self.shortid = self.id

        self.status = None
        self.error_msg = None
        if status is not None:
            self.status = (status == 1)
            self.error_msg = error_msg
    
    def to_str(self) -> str:
        """Convert the check to a string

        :returns: a string representing the check
        :rtype: str
        """
        status_and_error_msg = ""
        if self.status is not None:
            status_and_error_msg = ", status={}, error_msg={}".format(self.status, self.error_msg)

        return "CHECK(testsuite=\"{}\", id=\"{}\"{})".format(self.testsuite, self.id, status_and_error_msg)

    def __repr__(self) -> str:
        """Override of the __repr__ function used to output a string from an object

        :returns: a string representing the check
        :rtype: str
        """
        return self.to_str()

    def __str__(self) -> str:
        """Override of the __str__ function used to output a string from an object

        :returns: a string representing the check
        :rtype: str
        """
        return self.to_str()
    
    def __eq__(self, other) -> bool:
        """Override of the __eq__ function used to compare two Check objects

        :returns: a boolean indicating if the objects are equal
        :rtype: bool
        """
        return (isinstance(other, Check) and \
                self.testsuite == other.testsuite and \
                self.id == other.id and \
                self.status == other.status and \
                self.error_msg == other.error_msg)


def import_checks(path) -> list[Check]:
    """Imports checks from test source files

    :param path: path to the root of the test source files
    :type path: str

    :returns: a list of checks from the test source files
    :rtype: list[Check]
    """
    checks = []
    # Get the list of test source files
    files = glob.glob(path + "/**/*.cpp", recursive=True)
    for file in files:
        # Get the content of the test source file
        content = "".join(l[:-1] for l in open(file, encoding="utf-8"))
        # Find checks in the file
        for i in [m.start() for m in re.finditer(r"CHECK\([^\)]*\)", content)]:
            # The format of the check is
            #
            #     CHECK("<id>"...
            #           1    2
            cur = process_keyword(i, content)      # Go to 1
            cur, id = process_string(cur, content) # Go from 1 to 2

            # Recover the testsuite from the id
            testsuite, id = process_check_id(id)

            # Validate the testsuite and id
            if len(id.strip()) == 0:
                log_error("Missing id for test \"{}\" in file \"{}\"".format(content[i:cur], file))
                # The program is interrupted here as this is a critical error
                sys.exit(-1)

            # If no testsuite was provided or the provided testsuite is empty
            if testsuite is None:
                log_warn("Test \"{}\" doesn't have any parent testsuite".format(content[i:cur]))
            elif len(testsuite) == 0:
                log_error("Provided testsuite for test \"{}\" is empty".format(content[i:cur]))
                # The program is interrupted here as this is a critical error
                sys.exit(-1)

            checks += [Check(testsuite, id)]
    return checks 

def import_testdata(path: str) -> list[Check]:
    """Imports checks from the testdata files

    :param path: path to the root of the testdata files
    :type path: str

    :returns: a list of checks from the testdata files where the status is completed
    :rtype: list[Check]
    """
    checks = []
    # Get the list of testdata files
    files = glob.glob(path + "/*.csv")
    for file in files:
        with open(file, newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                # Skip empty lines or lines with only spaces
                if len(row) == 0 or (len(row) == 1 and len(row[0].strip()) == 0):
                    continue

                # The data is incomplete if no status is provided
                if len(row) < 2 or len(row[1].strip()) == 0:
                    log_error("Incomplete test data in {} for row \"{}\"".format(file, row))
                    # The program is interrupted here as this is a critical error
                    sys.exit(-1)
                # Read the check id from the testdata
                testsuite, id = process_check_id(row[0])
                # Add the check to the list providing both the status and error_msg parameters
                checks += [Check(testsuite, id, int(row[1]), (row[2] if len(row) >= 3 else None))]
    return checks

def process_check_id(raw_check_id: str) -> tuple[str, str]:
    """Converts a raw check id into both a the testsuite and the actual check id

    The format of the raw check id is : "testsuite.id"

    :param raw_check_id: raw check id
    :type raw_check_id: str

    :returns: a tuple containing both the testsuite and the id
    :rtype: tuple[str, str]
    """
    raw_check_id = raw_check_id.split(".")

    testsuite = None
    id = None
    if len(raw_check_id) == 1:
        id = raw_check_id[0]
    else:
        testsuite = raw_check_id[0]
        id = raw_check_id[1]
    return (testsuite, id)

def process_keyword(cur: int, content: str) -> int:
    """Increments cur to point to the char following the next parenthesis in content

    :param cur: pointer to the starting char in content
    :type cur: int

    :param content: content string
    :type content: str

    :returns: the incremented cur pointing to the char following the next parenthesis in content
    :rtype: int
    """
    cur_start = cur
    valid = True

    # Process the keyword
    keyword = "CHECK"
    for char in keyword:
        valid = valid & (content[cur] == char) 
        cur += 1
    # Process spaces
    while content[cur] == " ":
        cur += 1
    # Process the parenthesis
    valid = valid & (content[cur] == '(')
    cur += 1
    # Process spaces
    while content[cur] == " ":
        cur += 1
    valid = valid & (content[cur] == '\"')
    
    if not valid:
        log_error("Syntax error while processing keyword \"{}\"".format(content[cur_start:cur]))
        sys.exit(-1)

    return cur

def process_string(cur: int, content: str) -> tuple[int, str]:
    """Recovers a string contained between matching quotation marks starting from the char pointed by cur

    An empty string is returned in case where the first char pointed by cur is not a quotation mark

    :param cur: pointer to the starting char in content
    :type cur: int

    :param content: content string
    :type content: str

    :returns: a tuple containing both an incremented cur pointing to the next char after the quotation mark and the 
        recovered string
    :rtype: tuple[int, str]
    """
    cur_start = cur
    result = ""
    if content[cur] != "\"":
        log_error("Syntax error while running process_string. Missing starting \\\" while processing string \"{}\"" \
                    .format(content[cur_start:-1].replace("\"", "\\\"") + "..."))
        sys.exit(-1)

    cur += 1
    # We go up to the closing "
    while cur < len(content) and content[cur] != "\"":
        result += content[cur]
        cur += 1
    if cur == len(content):
        log_error("Syntax error while running process_string. Missing closing \" while processing string \"{}\"" \
                    .format(content[cur_start:-1].replace("\"", "\\\"") + "..."))
        sys.exit(-1)

    # Skip the closing \"
    cur += 1

    return cur, result
