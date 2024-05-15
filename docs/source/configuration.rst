Configuration
=============

The configuration is a JSON file that can be located anywhere in the project structure which specifies option values.

For example:

.. code-block:: json

   {
      "spec_dir_path": "relative/path1",
      "test_dir_path": "relative/path2",
      "testdata_dir_path": "/absolute/path1",
      "matrix_path": "/absolute/path2.csv",
      "spec_format": "RST",
      "disable_allocation": 1
   }

Configuration options
---------------------

The following options are allowed in the configuration of ECAP5-TREQ.

.. confval:: spec_dir_path

   Specifies the path to the directory containing sources of the specification where requirements will be imported from.

   :type: string path
   :required: Yes

   .. note::

      The search for source files is recursive and will result in importing requirements from source files in all subdirectories.

.. confval:: test_dir_path

   Specifies the path to the directory containing sources of the tests where checks will be imported from.

   :type: string path
   :required: Yes

   .. note::

      The search for source files is recursive and will result in importing checks from source files in all subdirectories.

.. confval:: testdata_dir_path

   Specifies the path to the directory containing testdata files.

   :type: string path
   :required: Yes

   .. note::

      The search for testdata files is recursive and will result in importing testdata from testdata files in all subdirectories.

.. confval:: matrix_path

   Specifies the path to the traceability matrix file.

   :type: string path
   :required: Yes

.. confval:: spec_format

   Specifies the language format of the specification source files.

   The following values are supported :
     - :code:`RST`: reStructuredText / Sphinx
     - :code:`TEX`: LaTeX

   :type: string spec_format
   :required: Yes

.. confval:: disable_allocation

   Disables the requirement allocation feature
