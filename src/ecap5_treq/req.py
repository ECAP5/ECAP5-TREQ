import sys
import re
import glob
from enum import Enum
from log import *

class ReqStatus:
    UNCOVERED = 0
    COVERED = 1
    UNTRACEABLE = 2

class Req:
    def __init__(self, id, description, options):
        self.id = id.replace("\\", "")
        self.description = description
        self.derivedFrom = None
        self.status = ReqStatus.UNCOVERED
        self.result = 0

        if options:
            if "derivedfrom" in options:
                self.derivedFrom = options["derivedfrom"]
                if len(self.derivedFrom) > 1:
                    log_error("Multiple values for option parameter \"derivedfrom\" of the \"{}\" are not allowed.".format(self.id))
                self.derivedFrom = self.derivedFrom[0].replace("\\", "")

    def __repr__(self):
        return "REQ(id=\"{}\", description=\"{}\", derivedFrom=\"{}\")".format(self.id, self.description, self.derivedFrom)

    def __str__(self):
        return "REQ(id=\"{}\", description=\"{}\", derivedFrom=\"{}\")".format(self.id, self.description, self.derivedFrom)

def process_keyword(cur, content):
    # Go to the next {
    while content[cur] != "{":
        cur += 1
    return cur

def process_matching_token(cur, content, opening_token, closing_token):
    # Skip spaces
    while content[cur] == " ":
        cur += 1
    # Return if the opening_token is not found
    if(content[cur] != opening_token):
        return (cur, None)

    result = ""
    cur += 1
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

def parse_reqs_in_file(filepath):
    reqlist = []
    content = "".join(l[:-1] for l in open(filepath))
    for i in [m.start() for m in re.finditer(r"\\req", content)]:
        cur = process_keyword(i, content)
        cur, id = process_matching_token(cur, content, "{", "}")
        cur, description = process_matching_token(cur, content, "{", "}")
        cur, options = process_matching_token(cur, content, "[", "]")

        if len(id) == 0:
            log_error("Missing id for requirement: \"{}\"".format(content[i:cur]))
        if not description or len(description) == 0:
            log_error("Missing description for requirement: \"{}\"".format(content[i:cur]))

        # convert the options string to a dictionary
        options_dict = None
        if options:
            options_dict = {}
            unjoined_options = options.split(",")
            joined_options = []
            # join elements when {
            current = []
            for op in unjoined_options:
                current += [op.strip()]
                # If we haven't seen any { yet
                if len(current) == 1:
                    if op.count('{') == op.count('}'):
                        joined_options += current
                        current = []
                else:
                    if op.count('{') < op.count('}'):
                        joined_options += [", ".join(current)]
                        current = []

            for op in joined_options:
                op = op.split("=")
                if(len(op) == 1):
                    log_error("Syntax error while processing requirement \"{}\"".format(id))
                # Elements from 1 to the end are joined with = to allow for the = character in the content of the option
                op_content = "=".join(op[1:]).strip()
                # Convert the content to a table
                op_content_tab = []
                if op_content[0] == '{':
                    op_content_tab = op_content[1:-1].split(", ")
                else:
                    op_content_tab = [op_content]
                options_dict[op[0].strip()] = op_content_tab

        reqlist += [Req(id, description, options_dict)]
    return reqlist

def extract_reqs(path):
    reqlist = []
    files = glob.glob(path + "/**/*.tex", recursive=True)
    for file in files:
        reqlist += parse_reqs_in_file(file)
    return reqlist

