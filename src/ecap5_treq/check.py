import re
import glob

class Check:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "CHECK(id=\"{}\")".format(self.id)

    def __str__(self):
        return "CHECK(id=\"{}\")".format(self.id)

def process_keyword(cur, content):
    # Go to the next (
    while content[cur] != "(":
        cur += 1
    return cur

def process_string(cur, content):
    result = ""
    cur += 1
    if content[cur] == "\"":
        cur += 1
        # We go up to the closing "
        while content[cur] != "\"":
            result += content[cur]
            cur += 1
    return cur, result

def parse_checks_in_file(filepath):
    checklist = []
    content = "".join(l[:-1] for l in open(filepath))
    for i in [m.start() for m in re.finditer(r"CHECK\([^\)]*\)", content)]:
        cur = process_keyword(i, content)
        cur, id = process_string(cur, content)

        checklist += [Check(id)]
    return checklist

def extract_checks(path):
    checklist = []
    files = glob.glob(path + "/**/*.cpp", recursive=True)
    for file in files:
        checklist += parse_checks_in_file(file)
    return checklist

