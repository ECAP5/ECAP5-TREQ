#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
# This file is part of ECAP5-TREQ <https://github.com/ECAP5/ECAP5-TREQ>
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

from ecap5_treq.log import log_error, log_warn
from ecap5_treq.config import SpecFormat

class ReqStatus:
    """A ReqStatus details the traceability status of requirements
    """
    UNCOVERED = "UNCOVERED"
    COVERED = "COVERED"
    UNTRACEABLE = "UNTRACEABLE"

class Req:
    """A Req represents a requirement
    """

    def __init__(self,                                    \
                 id: str,                                 \
                 description: str,                        \
                 options: dict[str, list[str]],           \
                 status: ReqStatus = ReqStatus.UNCOVERED, \
                 result: int = 0):
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
        self.allocation = None
        self.status = status
        self.result = result

        # Validate the requirement options
        if options:
            if "derivedfrom" in options:
                self.derived_from = [x for x in options["derivedfrom"]]
            if "allocation" in options:
                self.allocation = [x for x in options["allocation"]]

    def to_str(self) -> str:
        """Convert the req to a string

        :returns: a string representing the req 
        :rtype: str
        """
        return "REQ(id=\"{}\", description=\"{}\", derivedFrom=\"{}\", allocation=\"{}\", status={}, result={})" \
                    .format(self.id, self.description, self.derived_from, self.allocation, self.status, self.result)

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

    def __eq__(self, other) -> bool:
        """Override of the __eq__ function used to compare two Req objects

        :returns: a boolean indicating if the objects are equal
        :rtype: bool
        """
        return (isinstance(other, Req) and \
                self.id == other.id and \
                self.description == other.description and \
                self.derived_from == other.derived_from and \
                self.allocation == other.allocation and \
                self.status == other.status and \
                self.result == other.result)

def import_reqs(path: str, spec_format: SpecFormat) -> list[Req]:
    """Imports reqs from the specification source files

    :param path: path to the root of the specification source files
    :type path: str

    :param spec_format: language format of the specification
    :type spec_format: SpecFormat

    :returns: a list of checks from the specification source files
    :rtype: list[Req]
    """
    match spec_format:
        case SpecFormat.RST:
            return rst_import_reqs(path)
        case SpecFormat.TEX:
            return tex_import_reqs(path)
        case _:
            log_error("Unknown specification format: {}".format(spec_format))
            # The program is interrupted here as this is a critical error
            sys.exit(-1)

#
# rst parsing
#

def rst_import_reqs(path: str) -> list[Req]:
    """Imports reqs from the specification rst source files

    :param path: path to the root of the specification source files
    :type path: str

    :returns: a list of checks from the specification source files
    :rtype: list[Req]
    """
    reqs = []
    # Get the list of specification source files
    files = glob.glob(path + "/**/*.rst", recursive=True)
    for file in files:
        # Get the content of the specification source file
        lines = [l[:-1] for l in open(file, encoding="utf-8")]
        cur = 0
        while cur < len(lines):
            matches = list(re.finditer(r"\.\.\s*requirement::", lines[cur]))

            if len(matches) == 0:
                cur += 1
                continue

            cur, id      = rst_process_id(cur, lines)
            cur          = rst_skip_empty_lines(cur, lines)
            cur, options = rst_process_options(cur, lines)
            cur          = rst_skip_empty_lines(cur, lines)
            cur, desc    = rst_process_desc(cur, lines)

            if len(id) == 0:
                log_error("Missing id for requirement")
                # The program is interrupted here as this is a critical error
                sys.exit(-1)
            if len(("".join(desc.split("\n"))).strip()) == 0:
                log_warn("Missing description for requirement: \"{}\"".format(id))

            reqs += [Req(id, desc, options)]
    return reqs

def rst_process_id(cur: int, lines: list[str]) -> tuple[int, str]:
    """Processes the requirement id from the requirement directive line

    :param cur: pointer to the content's current line being processed
    :type cur: int

    :param lines: list of lines to process 
    :type lines: list[str]

    :returns: a tuple with both the incremented cur and the processed id
    :rtype: tuple[int, str]
    """
    line = lines[cur]
    # Move to the beginning of the id
    i = 0
    while line[i] != ":":
        i += 1
    i += 2

    # Extract the id up to the end of the line
    id = ""
    while i < len(line):
        id += line[i]
        i += 1
    
    id = id.strip()

    # Move to the next line
    cur += 1

    return (cur, id)

def rst_process_options(cur: int, lines: list[str]) -> tuple[int, dict[str, list[str]]]:
    """Processes the options if any

    :param cur: pointer to the content's current line being processed
    :type cur: int

    :param lines: list of lines to process 
    :type lines: list[str]

    :returns: a tuple with both the incremented cur and the processed options
    :rtype: tuple[int, dict[str, list[str]]]
    """
    optdict = {}
    # loop while there are options
    done = False
    while not done:
        cur = rst_skip_empty_lines(cur, lines)

        line = lines[cur]

        # skip tab
        i = 0
        while i < len(line) and line[i] == " ":
            i += 1

        # if no more option
        if line[i] != ':':
            done = True
            continue

        # skip :
        i += 1

        optid = ""
        # go to next :
        while i < len(line) and line[i] != ":":
            optid += line[i]
            i += 1

        # skip :
        i += 1

        optval = ""
        optval = [x.strip() for x in line[i:].split(",")]

        optdict[optid] = optval
        cur += 1
    return (cur, optdict)

def rst_process_desc(cur: int, lines: list[str]) -> tuple[int, str]:
    """Processes the description

    :param cur: pointer to the content's current line being processed
    :type cur: int

    :param lines: list of lines to process 
    :type lines: list[str]

    :returns: a tuple with both the incremented cur and the processed description
    :rtype: tuple[int, str]
    """
    desc = []
    # While the line is either empty of there are tabs
    while cur < len(lines) and (len(lines[cur]) == 0 or (lines[cur][0] == " ")):
        desc += [lines[cur]]
        cur += 1

    # Remove the empty trailing lines
    i = len(desc)-1
    while i > 0 and desc[i].strip() == "":
        i -= 1
    desc = [x.strip() for x in desc[0:i+1]]

    desc = "\n".join(desc)
    return (cur, desc)

def rst_skip_empty_lines(cur: int, lines: list[str]) -> int:
    """Advances the cursor to the next non-empty line

    :param cur: pointer to the content's current line being processed
    :type cur: int

    :param lines: list of lines to process 
    :type lines: list[str]

    :returns: the incremented cursor
    :rtype: tuple[int, str]
    """
    while lines[cur].strip() == "":
        cur += 1

    return cur

#
# tex parsing
#

def tex_import_reqs(path: str) -> list[Req]:
    """Imports reqs from the specification latex source files

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
        for i in [m.start() for m in re.finditer(r"\\req[\s]*{", content)]:
            # The format of the reqs is
            #
            #     \req{<id>}{<description>}[<options>]
            #         1     2              3         4
            cur = tex_process_keyword(i, content)                                 # Go to 1
            cur, id          = tex_process_matching_token(cur, content, "{", "}") # Go from 1 to 2
            cur, description = tex_process_matching_token(cur, content, "{", "}") # Go from 2 to 3
            cur, options     = tex_process_matching_token(cur, content, "[", "]") # Go from 3 to 4

            if len(id) == 0:
                log_error("Missing id for requirement: \"{}\"".format(content[i:cur]))
                # The program is interrupted here as this is a critical error
                sys.exit(-1)
            if not description or len(description) == 0:
                log_warn("Missing description for requirement: \"{}\"".format(content[i:cur]))

            # convert the options string to a dictionary
            options_dict = None
            if options:
                options_dict = tex_process_options(options)

            reqs += [Req(id, description, options_dict)]
    return reqs

def tex_process_keyword(cur: int, content: str) -> int:
    """Increments cur to point to the char following the next curly bracket in latex content

    :param cur: pointer to a char in content
    :type cur: int

    :param content: content string
    :type content: str

    :returns: the incremented cur pointing to the char following the next curly bracket in content
    :rtype: int
    """
    cur_start = cur
    # Go to the next {
    while cur < len(content) and content[cur] != "{":
        cur += 1

    if cur == len(content):
        log_error("Syntax error while processing keyword \"{}\"".format(content[cur_start:cur]))
        sys.exit(-1)

    return cur

def tex_process_matching_token(cur: int, content: str, opening_token: str, closing_token: str) -> tuple[int, str]:
    """Recovers a string containined in matching tokens provided as parameters for latex specification

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
    cur_start = cur

    # Return if the opening_token is not found
    if content[cur] != opening_token:
        return (cur, None)

    result = ""
    cur += 1
    # indent is used to keep track of the opened tokens waiting for their closing token
    ident = 1
    while cur < len(content) and ident > 0:
        if content[cur] == opening_token:
            ident += 1
        if content[cur] == closing_token:
            ident -= 1
        result += content[cur]
        cur += 1
    
    if cur == len(content) and ident > 0:
        log_error("Syntax error while processing matching tokens \"{}\"".format(content[cur_start:cur]))
        sys.exit(-1)

    # Remove the closing token
    result = result[:-1]
    return (cur, result.strip())

def tex_process_options(options: str) -> dict[str, list[str]]:
    """Converts the latex options string to a dictionary

    :param options: the options string
    :type options: str

    :returns: a dictionary containing the options
    :rtype: dict[str, list[str]]
    """
    options_dict = {}

    if len(options) == 0:
        return options_dict

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
        option_content_list = [x.replace("\\", "") for x in option_content_list]
        options_dict[option[0].strip()] = option_content_list
    return options_dict
