Traceability matrix
===================

Matrix generation
-----------------

The traceability matrix can be generated with the following command :

.. code-block:: bash

   ecap5-treq prepare_matrix -o <output_path>

In case where the matrix needs to be regenerated, providing the ``-m`` option will include the previous traceability data in the generated matrix :

.. code-block:: bash

   ecap5-treq prepare_matrix -m <previous_matrix_path> -o <output_path>

Matrix format
-------------

The traceability matrix is a table stored as csv file. On each row, the first cell is a check and the following checks are the requirements traced to the check. A additional rows marked as ``__UNTRACEABLE__`` contain requirements that shall be marked untraceable with a justification.

The following table is a representation of a sample traceability matrix :

.. list-table::

   * - ``check1``
     - ``req1``
     - ``req2``
     - ``req3``
   * - ``check2``
     - ``req4``
     - ``req5``
     - 
   * - ``check3``
     -
     -
     -
   * - ``check4``
     - ``req6``
     -
     -
   * - ``__UNTRACEABLE__``
     - ``req7``
     - ``justification for req7 being untraceable``
     -
   * - ``__UNTRACEABLE__``
     - ``req8``
     - ``justification for req8 being untraceable``
     -
