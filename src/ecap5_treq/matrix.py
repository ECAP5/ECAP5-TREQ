#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
# This file is part of ECAP5-TREQ <https://github.com/cchaine/ECAP5-TREQ>
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

import csv
import io

from ecap5_treq.check import Check
from ecap5_treq.req import Req

class Matrix:
    """A Matrix contains the traceability data between checks and requirements
    """

    def __init__(self, path = None):
        """Constructor of Matrix

        :param path: path to the traceability matrix file. The Matrix object will be empty if no path is provided
        :type: path: str
        """
        self.data = {}
        if path:
            self.read(path)

    def read(self, path: str) -> None:
        """Reads the traceability matrix from the file pointed by path

        :param path: path to the traceability matrix
        :type path: str

        :returns: a pointer to the read matrix
        :rtype: Matrix
        """
        self.data = {}
        with open(path, newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                # keep the content of the row if it was filled in
                if len(row) > 1:
                    self.data[row[0]] = row[1:]
                else:
                    self.data[row[0]] = []

    def check(self, checks: list[Check]) -> bool:
        """Checks if the checks in the matrix are strictly equal to the checks provided as parameter

        :param checks: the list of checks to verify against
        :type checks: list[Check]

        :returns: a boolean indicating the result of the comparison
        :rtype: bool
        """
        check_ids = [c.id for c in checks] + ["__UNTRACEABLE__"]
        matrix_ids = list(self.data.keys())

        check_ids.sort()
        matrix_ids.sort()
        
        return check_ids == matrix_ids
    
    def add(self, check_id: str, traced_reqs: list[Req]) -> None:
        """Adds traceability data to the matrix

        :param check_id: id of the check used to identify the traceability data
        :type check_id: str

        :param traced_reqs: list of requirements traced to the check_id
        :type traced_reqs: list[Req]
        """
        self.data[check_id] = traced_reqs

    def get(self, check_id: str) -> list[Req]:
        """Return the requirements traced to check_id
        
        :param check_id: id of the check used to identify the traceability data
        :type check_id: str

        :returns: the list of requirements traced to check_id
        :rtype: list[Req]
        """
        result = []
        if check_id in self.data:
            result = self.data[check_id]
        return result
    
    def __contains__(self, check_id: str) -> bool:
        """Override of the __contains__ function used to check if a check_id belongs to the traceability matrix
        
        :param check_id: id of the check used to identify the traceability data 
        :type check_id: str

        :returns: a boolean indicating if id of the check belongs to the traceability matrix
        :rtype: bool
        """
        return check_id in self.data
    
    def to_csv(self) -> str:
        """Converts this object to a csv string
        
        :returns: a csv string of the matrix
        :rtype: str
        """
        result = io.StringIO()
        writer = csv.writer(result, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for check_id in self.data:
            writer.writerow([check_id] + self.data[check_id])
        return result.getvalue()

    def __repr__(self):
        """Override of the __repr__ function used to output a string from an object

        :returns: a string representing the matrix
        :rtype: str
        """
        return self.to_csv()

    def __str__(self):
        """Override of the __str__ function used to output a string from an object

        :returns: a string representing the matrix
        :rtype: str
        """
        return self.to_csv()
    
    def __eq__(self, other):
        """Override of the __eq__ function used to compare two Matrix objects

        :returns: a boolean indicating if the objects are equal
        :rtype: bool
        """
        return (isinstance(other, Matrix) and \
                self.data == other.data)


def prepare_matrix(checks: list[Check], previous_matrix: Matrix) -> Matrix:
    """Generates an updated traceability matrix with an up-to-date list of checks.
    
    :param checks: list of checks to include in the matrix
    :type checks: list[Check]

    :param previous_matrix: previous matrix from which the previous traceability is recovered.
    :type previous_matrix: Matrix

    :returns: the updated traceability matrix
    :rtype: Matrix
    """
    if previous_matrix is None:
        previous_matrix = Matrix()

    matrix = Matrix()
    for check in checks:
        # write the check and add the previous matrix content if there was any
        matrix.add(check.id, previous_matrix.get(check.id))
    # add a row at the end for requirements that cannot be traced
    matrix.add("__UNTRACEABLE__", previous_matrix.get("__UNTRACEABLE__"))
    return matrix
