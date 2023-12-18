import re
import sys
import csv
import glob

class Check:
    def __init__(self, testsuite, id, status=None, errormsg=None):
        if testsuite:
            self.id = testsuite + "." + id
        else:
            self.id = id
        self.testsuite = testsuite
        self.shortid = id
        self.status = int(status) if status else None
        self.errormsg = errormsg

    def __repr__(self):
        status_and_error = ""
        if(self.status):
            status_and_error = ", status={}, errormsg={}".format(self.status, self.errormsg)
        return "CHECK(testsuite=\"{}\", id=\"{}\"{})".format(self.testsuite, self.id, status_and_error)

    def __str__(self):
        status_and_error = ""
        if(self.status):
            status_and_error = ", status={}, errormsg={}".format(self.status, self.errormsg)
        return "CHECK(testsuite=\"{}\", id=\"{}\"{})".format(self.testsuite, self.id, status_and_error)

def process_testsuite(s):
    raw_id = s.split(".")
    testsuite = None
    id = None
    if len(raw_id) == 1:
        print("WARN: Check {} doesn't have any parent testsuite".format(s), file=sys.stderr)
        id = raw_id[0]
    else:
        testsuite = raw_id[0]
        id = raw_id[1]
    return (testsuite, id)

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

        testsuite, id = process_testsuite(id)
        checklist += [Check(testsuite, id)]
    return checklist

def extract_checks(path):
    checklist = []
    files = glob.glob(path + "/**/*.cpp", recursive=True)
    for file in files:
        checklist += parse_checks_in_file(file)
    return checklist

def import_testdata(path):
    checks = []
    files = glob.glob(path + "/*.csv")
    for file in files:
        with open(file, newline='') as csvfile:
            r = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in r:
                if len(row) < 2:
                    print("ERROR: Incomplete test data in {}".format(file), file=sys.stderr)
                    sys.exit(-1)
                testsuite, id = process_testsuite(row[0])
                checks += [Check(testsuite, id, row[1], (row[2] if len(row) >= 3 else None))]
    return checks

