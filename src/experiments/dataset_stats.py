import os
import random

import numpy
import pandas
import tqdm

from src.experiments import datasets

DATA_DIR = os.getcwd() + 'data/'
PARSED_TRANSACTIONS_FILE = 'parsed_transactions.csv'
PARSED_ACCOUNTS_FILE = 'parsed_accounts.csv'
DATASET_STATS_RESULTS_DIR = os.getcwd() + '/results/dataset_stats/'

def get_avg_neighbors_at_distance(bank_data, sample_size, max_distance):
    account_id_samples = random.sample(bank_data.accounts['account_id'].tolist(), sample_size)
    data = numpy.array([get_neighbors_at_distance({account_id}, bank_data.transactions_by_origin, max_distance) for account_id in tqdm.tqdm(account_id_samples)])
    return data.mean(axis=0)

def get_neighbors_at_distance(starting_ids, transactions_by_origin, max_distance):
    current_ids = visited_ids = starting_ids
    current_hop = 1
    neighbors_at_distance = []

    while len(current_ids) > 0 and (current_hop <= max_distance):
        existing_origins = [current_id for current_id in current_ids if current_id in transactions_by_origin.index]
        current_transactions = transactions_by_origin.loc[existing_origins]
        current_ids = set(current_transactions['target_id']) - visited_ids
        visited_ids.update(current_ids)
        neighbors_at_distance.append(len(current_ids) + (0 if len(neighbors_at_distance) == 0 else neighbors_at_distance[-1]))
        current_hop += 1
    return neighbors_at_distance + [neighbors_at_distance[-1] for _ in range(max_distance - len(neighbors_at_distance))]

def count_in_out_stats(dataset):
    empty_dataframe = pandas.DataFrame(data=None, columns=list(set(dataset.transactions_by_origin.columns.to_list() + dataset.transactions_by_target.columns.to_list())))
    in_degree = []
    out_degree = []
    unique_in_degree = []
    unique_out_degree = []
    in_strength = []
    out_strength = []
    for _, account in tqdm.tqdm(dataset.accounts.iterrows(), total=len(dataset.accounts)):
        account_id = account['account_id']
        received = dataset.transactions_by_target.loc[[account_id]] if account_id in dataset.transactions_by_target.index else empty_dataframe
        sent = dataset.transactions_by_origin.loc[[account_id]] if account_id in dataset.transactions_by_origin.index else empty_dataframe
        if 'transaction_count' in dataset.transactions.columns:
            in_degree.append(received['transaction_count'].sum())
            out_degree.append(sent['transaction_count'].sum())
        else:
            in_degree.append(len(received))
            out_degree.append(len(sent))

        in_strength.append(received['amount'].sum())
        out_strength.append(sent['amount'].sum())

        unique_in_degree.append(len(set(received['origin_id'])))
        unique_out_degree.append(len(set(sent['target_id'])))

    return pandas.DataFrame({'account_id': dataset.accounts['account_id'], 'in_degree': in_degree, 'out_degree': out_degree, 'unique_in_degree': unique_in_degree, 'unique_out_degree': unique_out_degree, 'in_strength': in_strength, 'out_strength': out_strength, 'is_ml': dataset.accounts['is_ml'].to_list()}).sort_values(by='is_ml')

NEIGHBORS_AT_DISTANCE_SAMPLE_SIZE = 100
NEIGHBORS_AT_DISTANCE_MAX_DISTANCE = 10

def main():
    for dataset in datasets.get_datasets():
        print('Calculating out/in degree stats for ' + dataset.info.name)
        degree_stats = count_in_out_stats(dataset)
        degree_stats.to_csv(DATASET_STATS_RESULTS_DIR + dataset.info.name + '_stats.csv', index=False)

if __name__ == '__main__':
    main()