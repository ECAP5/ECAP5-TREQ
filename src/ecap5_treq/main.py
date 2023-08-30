import argparse
import glob
from parse import parse_reqs_in_file

def extract_reqs(path):
    reqlist = []
    files = glob.glob(path + "/**/*.tex", recursive=True)
    for file in files:
        reqlist += parse_reqs_in_file(file)
    return reqlist

def print_reqlist(reqlist):
    for req in reqlist:
        print("ID: {}\nDescription: {}\nOptions: {}\n".format(req.id, req.description, req.options))

def main():
    parser = argparse.ArgumentParser(
            prog="ECAP5-TREQ",
            description="Requirement and traceability management for ECAP5")
    parser.add_argument('path')
    args = parser.parse_args()

    reqs = extract_reqs(args.path)

if __name__ == "__main__":
    main()   
