import csv
import os

import tqdm

INPUT_FILE_NAME = 'transactions.csv'
OUTPUT_FILE_NAME = 'transactions_minimal.csv'
DATASET_DIRECTORY = 'amlsim/raw_data/'
DATA_DIRECTORY = os.getcwd() + '/data/'

def main():
    input_file_path = DATA_DIRECTORY + DATASET_DIRECTORY + INPUT_FILE_NAME
    output_file_path = DATA_DIRECTORY + DATASET_DIRECTORY + OUTPUT_FILE_NAME

    num_lines = sum(1 for _ in open(input_file_path))
    with open(input_file_path, newline='') as input_file, open(output_file_path, 'w') as output_file:
        reader = csv.reader(input_file, delimiter=',')
        for row in tqdm.tqdm(reader, total=num_lines):
            output_file.write(f'{row[1]},{row[2]},{row[4]},{row[-2]}\n')


if __name__ == '__main__':
    main()