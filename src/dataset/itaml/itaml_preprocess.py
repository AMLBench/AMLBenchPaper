import csv
import os

import tqdm

INPUT_FILE_NAME = 'HI-Large_Trans.csv'
OUTPUT_FILE_NAME = 'HI-Large_Trans_ach-only.csv'
DATASET_DIRECTORY = 'itaml/raw_data/'
DATA_DIRECTORY = os.getcwd() + '/data/'

def main():
    input_file_path = DATA_DIRECTORY + DATASET_DIRECTORY + INPUT_FILE_NAME
    output_file_path = DATA_DIRECTORY + DATASET_DIRECTORY + OUTPUT_FILE_NAME

    num_lines = sum(1 for _ in open(input_file_path))
    with open(input_file_path, newline='') as input_file, open(output_file_path, 'w') as output_file:
        reader = csv.reader(input_file, delimiter=',')
        output_file.write(','.join(next(reader)) + '\n')
        for row in tqdm.tqdm(reader, total=num_lines):
            transaction_type = row[-2]
            if transaction_type == 'ACH':
                output_file.write(','.join(row) + '\n')


if __name__ == '__main__':
    main()
