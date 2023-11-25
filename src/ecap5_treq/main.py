import argparse
from req import extract_reqs 
from check import extract_checks
import csv
import sys

def main():
    commands = ["extract_req", "extract_checks"]
    parser = argparse.ArgumentParser(
            prog="ECAP5-TREQ",
            description="Requirement and traceability management for ECAP5")
    parser.add_argument('command', choices = commands, 
                        metavar="command", 
                        help="The command to perform: {}".format(commands))
    parser.add_argument('path')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    if args.command == "extract_req":
        reqs = extract_reqs(args.path)
        for req in reqs:
            print(req)
    if args.command == "extract_checks":
        checks = extract_checks(args.path)
        for check in checks:
            print(check)
#    elif args.command == "report_test":
#        if args.output:
#            # Outputs to a csv file
#            with open(args.output, 'w', newline='') as csvfile:
#                w = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#                w.writerow(['Spam'] * 5 + ['Baked Beans'])
#                w.writerow(['Spam', 'Lovely Spam', 'Wondeful ,Spam'])
#
#            with open(args.output, newline='') as csvfile:
#                r = csv.reader(csvfile, delimiter=',', quotechar='|')
#                for row in r:
#                    print(row)

if __name__ == "__main__":
    main()   
