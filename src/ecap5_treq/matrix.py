import csv
import io

def prepare_matrix(checks, previous_matrix):
    matrix = {}
    matrix_str = io.StringIO()
    w = csv.writer(matrix_str, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for c in checks:
        # write the check and add the previous matrix content if there was any
        w.writerow([c.id] + (previous_matrix[c.id] if c.id in previous_matrix else []))
    # add a row at the end for requirements that cannot be traced
    w.writerow(["__UNTRACEABLE__"] + previous_matrix["__UNTRACEABLE__"] if "__UNTRACEABLE__" in previous_matrix else [])
    return matrix, matrix_str.getvalue()

def import_matrix(path):
    matrix = {}
    with open(path, newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in r:
            # keep the content of the row if it was filled in
            if len(row) > 1:
                matrix[row[0]] = row[1:]
            else:
                matrix[row[0]] = []
    return matrix

def check_matrix(matrix, checks):
    check_ids = [c.id for c in checks] + ["__UNTRACEABLE__"]
    matrix_ids = list(matrix.keys())

    check_ids.sort()
    matrix_ids.sort()
    
    return (check_ids == matrix_ids)
