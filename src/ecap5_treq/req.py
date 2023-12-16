import sys
import re
import glob

class Req:
    def __init__(self, id, description, options):
        self.id = id.replace("\\", "")
        self.description = description
        self.derivedFrom = None
        if options:
            if "derivedfrom" in options:
                self.derivedFrom = options["derivedfrom"].replace("\\", "")

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

        # convert the options string to a dictionary
        options_dict = None
        if options:
            options_dict = {}
            options = options.split(",")
            for op in options:
                op = op.split("=")
                if(len(op) == 1):
                    print("ERROR: Syntax error while processing {}".format(id), file=sys.stderr)
                # Elements from 1 to the end are joined with = to allow for the = character in the content of the option
                options_dict[op[0].strip()] = "=".join(op[1:]).strip()

        reqlist += [Req(id, description, options_dict)]
    return reqlist

def extract_reqs(path):
    reqlist = []
    files = glob.glob(path + "/**/*.tex", recursive=True)
    for file in files:
        reqlist += parse_reqs_in_file(file)
    return reqlist

