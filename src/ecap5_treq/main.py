import argparse
import os
from req import extract_reqs 
from check import Check, extract_checks, import_testdata
from report import generate_test_report, generate_test_summary
from matrix import import_matrix
from config import load_config, check_config
import csv
import sys
import glob

def rel_to_abs(path):
    if len(path) > 0:
        if path[0] != "/":
            path = os.path.abspath(os.getcwd()) + "/" + path
    return path

def cmd_print_reqs(config, args):
    check_config(config, ["spec_dir_path"])
    reqs = extract_reqs(config["spec_dir_path"])
    for req in reqs:
        print(req)

def cmd_print_checks(config, args):
    check_config(config, ["test_dir_path"])
    checks = extract_checks(config["test_dir_path"])
    for check in checks:
        print(check)

def cmd_prepare_matrix(config, args):
    check_config(config, ["test_dir_path"])

    # recover the previous matrix if specified
    matrix = {}
    if "matrix_path" in config:
        matrix = import_matrix(config["matrix_path"])

    checks = extract_checks(config["test_dir_path"])
    result = io.StringIO()
    w = csv.writer(result, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for c in checks:
        # write the check and add the previous matrix content if there was any
        w.writerow([c.id] + (matrix_content[c.id] if c.id in matrix_content else []))
    # add a row at the end for requirements that cannot be traced
    w.writerow(["__UNTRACEABLE__"])

    if(args.output):
        with open(args.output, 'w') as f:
            f.write(result)
    else:
        print(result)

def cmd_print_testdata(config, args):
    check_config(config, ["testdata_dir_path"])

    checks = import_testdata(config["testdata_dir_path"])
    for check in checks:
        print(check)

def cmd_gen_test_report(config, args):
    check_config(config, [
        "spec_dir_path",
        "test_dir_path",
        "testdata_dir_path",
        "matrix_path"
    ])

    reqs = extract_reqs(config["spec_dir_path"])
    checks = extract_checks(config["test_dir_path"])
    testdata = import_testdata(config["testdata_dir_path"])
    matrix = import_matrix(config["matrix_path"])
    report = generate_test_report(reqs, checks, testdata, matrix, args.format)
    if(args.output):
        with open(args.output, 'w') as f:
            f.write(report)
    else:
        print(report)

def cmd_gen_test_summary(config, args):
    check_config(config, [
        "spec_dir_path",
        "test_dir_path",
        "testdata_dir_path",
        "matrix_path"
    ])

    reqs = extract_reqs(config["spec_dir_path"])
    checks = extract_checks(config["test_dir_path"])
    testdata = import_testdata(config["testdata_dir_path"])
    matrix = import_matrix(config["matrix_path"])
    report = generate_test_summary(reqs, checks, testdata, matrix, args.format)
    if(args.output):
        with open(args.output, 'w') as f:
            f.write(report)
    else:
        print(report)

def main():
    parser = argparse.ArgumentParser(
            prog="ECAP5-TREQ",
            description="Requirement and traceability management for ECAP5")
    parser.add_argument('command')
    parser.add_argument('-c', '--config')
    parser.add_argument("-f", "--format", default="html")
    parser.add_argument('-s', '--spec')
    parser.add_argument('-t', '--tests')
    parser.add_argument('-d', '--data' )
    parser.add_argument('-m', '--matrix')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    config = {}
    if(args.config):
        config = load_config(args.config)
    else:
        config["spec_dir_path"] = args.spec
        config["test_dir_path"] = args.tests
        config["testdata_dir_path"] = args.data
        config["matrix_path"] = args.matrix

    # convert relative paths to absolute paths
    config["spec_dir_path"]      =  rel_to_abs(config["spec_dir_path"])
    config["test_dir_path"]      =  rel_to_abs(config["test_dir_path"])
    config["testdata_dir_path"]  =  rel_to_abs(config["testdata_dir_path"])
    config["matrix_path"]        =  rel_to_abs(config["matrix_path"])

    if args.command == "print_reqs":
        cmd_print_reqs(config, args)
    elif args.command == "print_checks":
        cmd_print_checks(config, args)
    elif args.command == "prepare_matrix":
        cmd_prepare_matrix(config, args)
    elif args.command == "print_testdata":
        cmd_print_testdata(config, args)
    elif args.command == "gen_test_report":
        cmd_gen_test_report(config, args)
    elif args.command == "gen_test_summary":
        cmd_gen_test_summary(config, args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()   
