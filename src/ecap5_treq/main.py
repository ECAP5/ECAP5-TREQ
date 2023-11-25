import argparse
from req import extract_reqs 
from check import Check, extract_checks, import_testdata
from report import generate_html_report
import csv
import sys
import glob

def cmd_print_reqs(args):
    reqs = extract_reqs(args.spec)
    for req in reqs:
        print(req)

def cmd_print_checks(args):
    checks = extract_checks(args.tests)
    for check in checks:
        print(check)

def cmd_prepare_matrix(args):
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

def cmd_print_testdata(args):
    checks = import_testdata(args.data)
    for check in checks:
        print(check)

def cmd_gen_report(args):
    checks = import_testdata(args.data)
    generate_html_report(checks)

def main():
    parser = argparse.ArgumentParser(
            prog="ECAP5-TREQ",
            description="Requirement and traceability management for ECAP5")
    subparsers = parser.add_subparsers(help='commands', dest='command')

    parser_print_reqs = subparsers.add_parser('print_reqs')
    parser_print_reqs.add_argument('-s', '--spec')

    parser_print_checks = subparsers.add_parser('print_checks')
    parser_print_checks.add_argument('-t', '--tests')

    parser_prepare_matrix = subparsers.add_parser('prepare_matrix')
    parser_prepare_matrix.add_argument('-t', '--tests', required=True)
    parser_prepare_matrix.add_argument('-m', '--matrix')
    parser_prepare_matrix.add_argument('-o', '--output', required=True)

    parser_print_testdata = subparsers.add_parser('print_testdata')
    parser_print_testdata.add_argument('-d', '--data', required=True)

    parser_print_testdata = subparsers.add_parser('gen_report')
    parser_print_testdata.add_argument('-d', '--data', required=True)

    args = parser.parse_args()

    if args.command == "print_reqs":
        cmd_print_reqs(args)
    if args.command == "print_checks":
        cmd_print_checks(args)
    if args.command == "prepare_matrix":
        cmd_prepare_matrix(args)
    if args.command == "print_testdata":
        cmd_print_testdata(args)
    if args.command == "gen_report":
        cmd_gen_report(args)

if __name__ == "__main__":
    main()   
