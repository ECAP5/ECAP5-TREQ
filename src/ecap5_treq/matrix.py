import csv

def import_matrix(path):
    matrix = {}
    with open(path, newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in r:
            # keep the content of the row if it was filled in
            if len(row) > 1:
                matrix[row[0]] = row[1:]
    return matrix
