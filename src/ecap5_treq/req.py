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

import sys
import re
import glob

from ecap5_treq.log import log_error

class ReqStatus:
    """A ReqStatus details the traceability status of requirements
    """
    UNCOVERED = 0
    COVERED = 1
    UNTRACEABLE = 2

class Req:
    """A Req represents a requirement
    """

    def __init__(self, id: str, description: str, options: dict[str, list[str]]):
        """Constructor of Req 

        :param id: identifier of the requirement
        :type id: str

        :param description: description of the requirement
        :type description: str

        :param options: a dictionary containing the options of the requirement
        :type options: dict[str, list[str]]
        """
        self.id = id.replace("\\", "")
        self.description = description
        self.derived_from = None
        self.status = ReqStatus.UNCOVERED
        self.result = 0

        # Validate the requirement options
        if options:
            if "derivedfrom" in options:
                self.derived_from = options["derivedfrom"]
                if len(self.derived_from) > 1:
                    log_error("Multiple values for option parameter \"derivedfrom\" of the \"{}\" are not allowed." \
                                .format(self.id))
                self.derived_from = self.derived_from[0].replace("\\", "")

    def to_str(self) -> str:
        """Convert the req to a string

        :returns: a string representing the req 
        :rtype: str
        """
        return "REQ(id=\"{}\", description=\"{}\", derivedFrom=\"{}\")" \
                    .format(self.id, self.description, self.derived_from)

    def __repr__(self):
        """Override of the __repr__ function used to output a string from an object

        :returns: a string representing the req 
        :rtype: str
        """
        return self.to_str()

    def __str__(self):
        """Override of the __str__ function used to output a string from an object

        :returns: a string representing the req 
        :rtype: str
        """
        return self.to_str()

def import_reqs(path: str) -> list[Req]:
    """Imports reqs from the specification source files

    :param path: path to the root of the specification source files
    :type path: str

    :returns: a list of checks from the specification source files
    :rtype: list[Req]
    """
    reqs = []
    # Get the list of specification source files
    files = glob.glob(path + "/**/*.tex", recursive=True)
    for file in files:
        # Get the content of the specification source file
        content = "".join(l[:-1] for l in open(file, encoding="utf-8"))
        # Find reqs in the file
        for i in [m.start() for m in re.finditer(r"\\req", content)]:
            # The format of the reqs is
            #
            #     \req{<id>}{<description>}[<options>]
            #         1     2              3         4
            cur = process_keyword(i, content)                                 # Go to 1
            cur, id          = process_matching_token(cur, content, "{", "}") # Go from 1 to 2
            cur, description = process_matching_token(cur, content, "{", "}") # Go from 2 to 3
            cur, options     = process_matching_token(cur, content, "[", "]") # Go from 3 to 4

            if len(id) == 0:
                log_error("Missing id for requirement: \"{}\"".format(content[i:cur]))
                # The program is interrupted here as this is a critical error
                sys.exit(-1)
            if not description or len(description) == 0:
                log_error("Missing description for requirement: \"{}\"".format(content[i:cur]))

            # convert the options string to a dictionary
            options_dict = None
            if options:
                options_dict = process_options(options)

            reqs += [Req(id, description, options_dict)]
    return reqs

def process_keyword(cur: int, content: str) -> int:
    """Increments cur to point to the char following the next curly bracket in content

    :param cur: pointer to a char in content
    :type cur: int

    :param content: content string
    :type content: str

    :returns: the incremented cur pointing to the char following the next curly bracket in content
    :rtype: int
    """
    # Go to the next {
    while content[cur] != "{":
        cur += 1
    return cur

def process_matching_token(cur: int, content: str, opening_token: str, closing_token: str) -> tuple[int, str]:
    """Recovers a string containined in matching tokens provided as parameters

    :param cur: pointer to the starting char in content
    :type cur: int

    :param content: content string
    :type content: str
    
    :param opening_token: opening token used for the token matching
    :type opening_token: str

    :param closing_token: closing token used for the token matching
    :type closing_token: str

    :returns: a tuple containing both an incremented cur pointing to the next char fater the closing token and the 
        recovered string
    :rtype: tuple[int, str]
    """
    # Skip spaces
    while content[cur] == " ":
        cur += 1

    # Return if the opening_token is not found
    if content[cur] != opening_token:
        return (cur, None)

    result = ""
    cur += 1
    # indent is used to keep track of the opened tokens waiting for their closing token
    ident = 1
    while ident > 0:
        if content[cur] == opening_token:
            ident += 1
        if content[cur] == closing_token:
            ident -= 1
        result += content[cur]
        cur += 1
    result = result[:-1]
    return (cur, result.strip())

def process_options(options: str) -> dict[str, list[str]]:
    """Converts the options string to a dictionary

    :param options: the options string
    :type options: str

    :returns: a dictionary containing the options
    :rtype: dict[str, list[str]]
    """
    options_dict = {}

    # Options can have a comma within their content if surrounded by curly brackets
    # Join options when curly brackets are used within the option
    unjoined_options = options.split(",")
    joined_options = []
    current = []
    for option in unjoined_options:
        current += [option.strip()]
        # If we haven't seen any { yet
        if len(current) == 1:
            # If there is no remaining opening curly bracket
            if option.count('{') == option.count('}'):
                # Consider the option joined
                joined_options += current
                current = []
        else:
            # If there more closing curly brackets than opening
            if option.count('{') < option.count('}'):
                # Consider the option joined
                joined_options += [", ".join(current)]
                current = []

    for option in joined_options:
        # Split the option key and the option content
        option = option.split("=")
        if len(option) == 1:
            log_error("Syntax error while processing requirement \"{}\"".format(id))
                # The program is interrupted here as this is a critical error
            sys.exit(-1)

        # Elements from 1 to the end are joined with = to allow for the = character in the content of the option
        option_content = "=".join(option[1:]).strip()

        # Convert the content to a table
        option_content_list = []
        if option_content[0] == '{':
            # Remove the surrounding curly brackets if any
            option_content_list = option_content[1:-1].split(", ")
        else:
            option_content_list = [option_content]
        options_dict[option[0].strip()] = option_content_list
    return options_dict
