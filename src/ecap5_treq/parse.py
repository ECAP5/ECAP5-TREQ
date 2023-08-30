import re
from req import Req

def process_keyword(cur, content):
    # Go to the next {
    while content[cur] != "{":
        cur += 1
    return cur

def process_matching_token(cur, content, opening_token, closing_token):
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
    return (cur, result)

def process_options(cur, content):
    # Skip spaces
    while content[cur] == " ":
        cur += 1
    if(content[cur] == "["):
        return process_matching_token(cur, content, "[", "]")
    else:
        return (cur, None)

def parse_reqs_in_file(filepath):
    reqlist = []
    content = "".join(l[:-1] for l in open(filepath))
    for i in [m.start() for m in re.finditer(r"\\req", content)]:
        cur = process_keyword(i, content)
        cur, id = process_matching_token(cur, content, "{", "}")
        cur, description = process_matching_token(cur, content, "{", "}")
        cur, options = process_options(cur, content)
        
        reqlist += [Req(id, description, options)]
    return reqlist
