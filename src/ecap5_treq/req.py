import argparse
import glob
import re

class Req:
    regex = re.compile(r"\\req\{([^\}]*)\}\{([^\}]*)\}\[([^\]]*)\]")

    def __init__(self, id, description, additionals):
        self.id = id
        self.description = description
        self.additionals = additionals

def find_req_in_file(filepath):
    reqlist = []
    content = "".join(l[:-1] for l in open(filepath))
    return reqlist

def extract_reqs(path):
    reqlist = []
    files = glob.glob(path + "/**/*.tex", recursive=True)
    for file in files:
        reqlist += find_req_in_file(file)
    print_reqlist(reqlist)

def print_reqlist(reqlist):
    for req in reqlist:
        print("ID: {}\nDescription: {}\n\n".format(req.id, req.description))

def main():
    parser = argparse.ArgumentParser(
            prog="ECAP5-TREQ",
            description="Requirement and traceability management for ECAP5")
    parser.add_argument('path')
    args = parser.parse_args()

    extract_reqs(args.path)

if __name__ == "__main__":
    main()   
