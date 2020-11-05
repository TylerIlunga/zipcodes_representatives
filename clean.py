import csv
from os import getcwd

INPUT_CSV_DATA_PATH = getcwd() + '/data/zipcode_data.csv'
OUTPUT_CSV_DATA_PATH = getcwd() + '/data/zipcode_data_clean.csv'


def remove_rows_with_no_rep():
    with open(INPUT_CSV_DATA_PATH, 'r') as input, open(OUTPUT_CSV_DATA_PATH, 'w', newline='') as output:
        reader = csv.reader(input, skipinitialspace=True)
        writer = csv.writer(output, delimiter=",")
        for row in reader:
            if row[2] == "" or row[2] == None:
                continue
            writer.writerow(row)


remove_rows_with_no_rep()
