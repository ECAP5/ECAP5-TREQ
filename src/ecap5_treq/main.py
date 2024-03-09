#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
# This file is part of ECAP5-TREQ <https://github.com/ECAP5/ECAP5-TREQ>
# 
# ECAP5-TREQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ECAP5-TREQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ECAP5-TREQ.  If not, see <http://www.gnu.org/licenses/>.

import argparse

from ecap5_treq.analysis import Analysis
from ecap5_treq.check import import_checks, import_testdata
from ecap5_treq.config import Config
from ecap5_treq.log import log_error
from ecap5_treq.matrix import Matrix, prepare_matrix
from ecap5_treq.report import generate_report_warning_section,  \
                              generate_report_summary,          \
                              generate_test_report,             \
                              generate_traceability_report,     \
                              generate_test_result_badge,       \
                              generate_traceability_result_badge                                                               
from ecap5_treq.req import import_reqs 
from ecap5_treq.html import markdown_to_html

def cmd_print_reqs(config: dict[str, str]) -> None:
    """Handles the print_reqs command.

    The print_reqs command prints a list of the requirements from the specification which path
    is given in config

    :param config: a configuration dictionnary providing path to input files
    :type config: dict[str, str]
    """
    reqs = import_reqs(config.get("spec_dir_path"))
    for req in reqs:
        print(req)

def cmd_print_checks(config: dict[str, str]) -> None:
    """Handles the print_checks command.

    The print_checks command prints a list of the checks from the tests which path
    is given in config

    :param config: a configuration dictionnary providing path to input files
    :type config: dict[str, str]
    """
    checks = import_checks(config.get("test_dir_path"))
    for check in checks:
        print(check)

def cmd_print_testdata(config: dict[str, str]) -> None:
    """Handles the print_testdata command.

    The print_testdata command prints a list of checks including their status from the testdata
    which path is given in config

    :param config: a configuration dictionnary providing path to input files
    :type config: dict[str, str]
    """
    checks = import_testdata(config.get("testdata_dir_path"))
    for check in checks:
        print(check)

def cmd_prepare_matrix(config: dict[str, str]) -> None:
    """Handles the prepare_matrix command.

    The prepare matrix command generates an updated traceability matrix with an up-to-date list of
    checks.

    :param config: a configuration dictionnary providing path to input files
    :type config: dict[str, str]
    """
    # recover the previous matrix if specified
    previous_matrix = Matrix()
    if "matrix_path" in config:
        previous_matrix.read(config.get("matrix_path"))

    checks = import_checks(config.get("test_dir_path"))
    matrix = prepare_matrix(checks, previous_matrix)

    if "output" in config:
        with open(config.get("output"), 'w', encoding="utf-8") as file:
            file.write(matrix.to_csv())
    else:
        print(matrix.to_csv())

def cmd_gen_report(config: dict[str, str]) -> None:
    """Handles the gen_report command.

    The gen_report command generates a markdown test and traceability report.

    :param config: a configuration dictionnary providing path to input files
    :type config: dict[str, str]
    """
    reqs = import_reqs(config.get("spec_dir_path"))
    checks = import_checks(config.get("test_dir_path"))
    testdata = import_testdata(config.get("testdata_dir_path"))
    matrix = Matrix(config.get("matrix_path"))
    # Perform the test result and traceability analysis
    analysis = Analysis(reqs, checks, testdata, matrix)

    # Generate report sections
    report_warnings = generate_report_warning_section()
    report_summary = generate_report_summary(analysis)
    test_report = generate_test_report(analysis)
    traceability_report = generate_traceability_report(analysis)

    # Only output the full report if there are no error messages
    if len(log_error.msgs) > 0:
        report = report_warnings + "\n**Report generation failed.**"
    else:
        report = report_warnings + report_summary + test_report + traceability_report

    # Convert to html if requested
    if config.get("html"):
        report = markdown_to_html(report)

    if "output" in config:
        with open(config.get("output"), 'w', encoding="utf-8") as file:
            file.write(report)
    else:
        print(report)

def cmd_gen_test_result_badge(config: dict[str, str]) -> None:
    """Handles the gen_test_result_badge command.

    The gen_test_result_badge command generates a json for configuring the generation of
    an svg badge by img.shields.io for the test results

    :param config: a configuration dictionnary providing path to input files
    :type config: dict[str, str]
    """
    reqs = import_reqs(config.get("spec_dir_path"))
    checks = import_checks(config.get("test_dir_path"))
    testdata = import_testdata(config.get("testdata_dir_path"))
    matrix = Matrix(config.get("matrix_path"))
    # Perform the test result and traceability analysis
    analysis = Analysis(reqs, checks, testdata, matrix)

    # Generate a test result badge
    badge = generate_test_result_badge(analysis)

    if "output" in config:
        with open(config.get("output"), 'w', encoding="utf-8") as file:
            file.write(badge)
    else:
        print(badge)

def cmd_gen_traceability_result_badge(config: dict[str, str]) -> None:
    """Handles the gen_traceability_result_badge command.

    The gen_traceability_result_badge command generates a json for configuring the generation of
    an svg badge by img.shields.io for the traceability results

    :param config: a configuration dictionnary providing path to input files
    :type config: dict[str, str]
    """
    reqs = import_reqs(config.get("spec_dir_path"))
    checks = import_checks(config.get("test_dir_path"))
    testdata = import_testdata(config.get("testdata_dir_path"))
    matrix = Matrix(config.get("matrix_path"))
    # Perform the test result and traceability analysis
    analysis = Analysis(reqs, checks, testdata, matrix)

    # Generate a traceability result badge
    badge = generate_traceability_result_badge(analysis)

    if "output" in config:
        with open(config.get("output"), 'w', encoding="utf-8") as file:
            file.write(badge)
    else:
        print(badge)

def main():
    """Entry point to ECAP5-TREQ
    """
    # Configure command line arguments
    parser = argparse.ArgumentParser(
            prog="ECAP5-TREQ",
            description="Requirement and traceability management for ECAP5",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
The command option expects one of the following:
    print_reqs                       Prints a list of requirements extracted from the source files of the 
                                     specification.
    print_checks                     Prints a list of checks extracted from the source files of the tests.
    print_testdata                   Prints a list of checks extracted from the testdata. These checks include test 
                                     results and potential error messages.
    prepare_matrix                   Generates a matrix with checks extracted from the source files of the tests.
    gen_report                       Generates a test and traceability report markdown report.
    gen_test_result_badge            Generates a JSON file for configuring the generation of a test result svg 
                                     badge by img.shields.io.
    gen_traceability_result_badge    Generates a JSON file for configuring the generation of a traceability result 
                                     svg badge by img.shields.io

The full documentation is available at https://ecap5.github.io/ECAP5-TREQ/index.html""")
    parser.add_argument('command')
    parser.add_argument('-c', '--config')
    parser.add_argument('-s', '--spec')
    parser.add_argument('-t', '--tests')
    parser.add_argument('-d', '--data' )
    parser.add_argument('-m', '--matrix')
    parser.add_argument('-o', '--output')
    parser.add_argument('--html', action='store_true')

    args = parser.parse_args()

    # Create a config object storing the configuration parameters
    config = Config(args.config)

    # Command line arguments override the configuration
    if args.spec:
        config.set_path("spec_dir_path", args.spec)
    if args.tests:
        config.set_path("test_dir_path", args.tests)
    if args.data:
        config.set_path("testdata_dir_path", args.data)
    if args.matrix:
        config.set_path("matrix_path", args.matrix)
    
    # Add other arguments that are not present in configuration files
    if args.output:
        config.set("output", args.output)
    config.set("html", args.html)
    
    # Handle the different commands provided
    if args.command == "print_reqs":
        cmd_print_reqs(config)
    elif args.command == "print_checks":
        cmd_print_checks(config)
    elif args.command == "print_testdata":
        cmd_print_testdata(config)
    elif args.command == "prepare_matrix":
        cmd_prepare_matrix(config)
    elif args.command == "gen_report":
        cmd_gen_report(config)
    elif args.command == "gen_test_result_badge":
        cmd_gen_test_result_badge(config)
    elif args.command == "gen_traceability_result_badge":
        cmd_gen_traceability_result_badge(config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
