import argparse
from req import extract_reqs 
from check import Check, extract_checks
import csv
import sys
import glob

def main():
    commands = ["extract_req", "extract_checks", "prepare_matrix", "read_testdata", "gen_report"]
    parser = argparse.ArgumentParser(
            prog="ECAP5-TREQ",
            description="Requirement and traceability management for ECAP5")
    parser.add_argument('command', choices = commands, 
                        metavar="command", 
                        help="The command to perform: {}".format(commands))
    parser.add_argument('-s', '--spec', required=True)
    parser.add_argument('-t', '--tests', required=True)
    parser.add_argument('-d', '--data', required=True)
    parser.add_argument('-m', '--matrix')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    if args.command == "extract_req":
        reqs = extract_reqs(args.spec)
        for req in reqs:
            print(req)
    if args.command == "extract_checks":
        checks = extract_checks(args.tests)
        for check in checks:
            print(check)
    if args.command == "prepare_matrix":
        if not args.output:
            print("ERROR: The output parameter is required for the prepare_matrix command.\n")
            parser.print_help()
            sys.exit(-1)

        # recover the previous matrix if specified
        matrix_content = {}
        if args.matrix:
            with open(args.matrix, newline='') as csvfile:
                r = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in r:
                    # keep the content of the row if it was filled in
                    if len(row) > 1:
                        matrix_content[row[0]] = row[1:]

        checks = extract_checks(args.tests)
        with open(args.output, 'w', newline='') as csvfile:
            w = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for c in checks:
                # write the check and add the previous matrix content if there was any
                w.writerow([c.id] + (matrix_content[c.id] if c.id in matrix_content else []))
            # add a row at the end for requirements that cannot be traced
            w.writerow(["__UNTRACEABLE__"])
    if args.command == "read_testdata":
        checks = []
        files = glob.glob(args.data + "/tb_*.csv")
        for file in files:
            with open(file, newline='') as csvfile:
                r = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in r:
                    if len(row) < 2:
                        print("ERROR: Incomplete test data in {}".format(file))
                        sys.exit(-1)
                    checks += [Check(row[0], row[1], (row[2] if len(row) >= 3 else None))]
        for check in checks:
            print(check)
    if args.command == "gen_report":
        print("gen_report")
          

if __name__ == "__main__":
    main()   
