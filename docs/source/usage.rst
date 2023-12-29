Usage
=====

ECAP5-TREQ is a command-line tool which can be run as follows:

.. code-block:: bash

   ecap5-treq <command> <options>

Commands
--------

.. option:: print_reqs

   Prints a list of requirements extracted from the source files of the specification.

.. option:: print_checks

   Prints a list of checks extracted from the source files of the tests.

.. option:: print_testdata

   Prints a list of checks extracted from the testdata. These checks include test results and potential error messages.

.. option:: prepare_matrix

   Generates a matrix with checks extracted from the source files of the tests.
   
   .. note::

      If a path to the previous matrix was provided, the generated matrix will be filled with the previous traceability data.

.. option:: gen_report

   Generates a test and traceability report markdown report.

.. option:: gen_test_result_badge

   Generates a JSON file for configuring the generation of a test result svg badge by img.shields.io.

.. option:: gen_traceability_result_badge

   Generates a JSON file for configuring the generation of a traceability result svg badge by img.shields.io.

Options
-------

The following command-line options can be provided to ECAP5-TREQ.

.. warning::

   Command-line options override the options provided in the configuration file.

.. option:: -c <config_path>, --config <config_path>

   Path to the configuration file.

.. option:: -s <spec_dir_path>, --spec <spec_dir_path>

   Path to the directory containing sources of the specification where requirements will be imported from.

   .. note::

      The search for source files is recursive and will result in importing requirements from source files in all subdirectories.

.. option:: -t <test_dir_path>, --tests <test_dir_path>

   Path to the directory containing sources of the tests where checks will be imported from.

   .. note::

      The search for source files is recursive and will result in importing checks from source files in all subdirectories.

.. option:: -d <testdata_dir_path>, --data <testdata_dir_path>

   Path to the directory containing testdata files.

   .. note::

      The search for testdata files is recursive and will result in importing testdata from testdata files in all subdirectories.

.. option:: -m <matrix_path>, --matrix <matrix_path>

   Path to the traceability matrix file.

.. option:: -o <output_path>, --output <output_path>

   Path to the output file where the result will be written.

   .. note::
      The result is outputed to ``stdout`` if no output is provided.

