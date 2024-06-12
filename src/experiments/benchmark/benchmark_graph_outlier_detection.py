import logging
import os
import traceback
import numpy
import pandas
import torch
from pygod.detector import DOMINANT, SCAN, Radar, GAE, ONE, OCGNN, GUIDE, GAAN, DONE, CONAD, CoLA, AdONE, ANOMALOUS, \
    AnomalyDAE
from sklearn.metrics import precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler
from torch_geometric.data import Data
import tqdm

from src.experiments import datasets
from src.tools import logger_manager

DATA_DIR = os.getcwd() + 'data/'
CASES_SINGLE_TRANSACTION = DATA_DIR + 'cases_single_transaction/parsed_data/'
CASES_MULTI_TRANSACTION = DATA_DIR + 'cases_multi_transaction/parsed_data/'
AML_SIM_DIR = DATA_DIR + 'amlsim/10k_dataset/parsed_data/'
RABO_DIR = DATA_DIR + 'rabo/parsed_data/'
BERKA_DIR = DATA_DIR + 'berka/parsed_data/'
CASES_DIR = DATA_DIR + 'cases/parsed_data/'

PARSED_TRANSACTIONS_FILE = 'parsed_transactions.csv'
PARSED_ACCOUNTS_FILE = 'parsed_accounts.csv'

DATASET_STATS_RESULTS_DIR = os.getcwd() + '/results/dataset_stats/'

DEFAULT_PYGOD_EPOCHS = 100
DEFAULT_PYGOD_VERBOSE = True
DEFAULT_PYGOD_PARAMS = {'gpu': 0, 'verbose': DEFAULT_PYGOD_VERBOSE, 'epoch': DEFAULT_PYGOD_EPOCHS}

N_RUNS = 5

PYGOD_OUTLIER_DETECTION_METHODS = [#(AdONE, 'AdONE', DEFAULT_PYGOD_PARAMS),
                                   #(ANOMALOUS, 'ANOMALOUS', DEFAULT_PYGOD_PARAMS),
                                   #(AnomalyDAE, 'AnomalyDAE', DEFAULT_PYGOD_PARAMS),
                                   #(CoLA, 'CoLA', DEFAULT_PYGOD_PARAMS),
                                   #(CONAD, 'CONAD', DEFAULT_PYGOD_PARAMS),
                                   #(DOMINANT, 'DOMINANT', DEFAULT_PYGOD_PARAMS),
                                   #(DONE, 'DONE', DEFAULT_PYGOD_PARAMS),
                                   #(GAAN, 'GAAN', DEFAULT_PYGOD_PARAMS),
                                   (GAE, 'GAE', {'gpu': -1, 'verbose': DEFAULT_PYGOD_VERBOSE, 'epoch': DEFAULT_PYGOD_EPOCHS}),
                                   #(GUIDE, 'GUIDE', DEFAULT_PYGOD_PARAMS),
                                   (OCGNN, 'OCGNN', DEFAULT_PYGOD_PARAMS),
                                   #(ONE, 'ONE', DEFAULT_PYGOD_PARAMS),
                                   #(Radar, 'Radar', DEFAULT_PYGOD_PARAMS),
                                   #(SCAN, 'Scan', DEFAULT_PYGOD_PARAMS),
                                   ]

def benchmark_graph_outlier_detection():
    for dataset in datasets.get_datasets():
        dataset_stats = pandas.read_csv(DATASET_STATS_RESULTS_DIR + dataset.info.name + '_stats.csv').sample(frac=1)
        contamination = dataset_stats['is_ml'].sum() / len(dataset_stats)
        for method, params in PYGOD_OUTLIER_DETECTION_METHODS:
            total_precision = []
            total_recall = []
            total_f = []
            total_y_pred_count = []
            total_y_true_count = []
            try:
                for _ in tqdm.tqdm(range(N_RUNS)):
                    logging.info(f'Applying {str(method)} to {dataset.info.name}')
                    precision, recall, y_true_count, y_pred_count, f_score = apply_graph_outlier_detector(dataset.transactions, dataset_stats, method(contamination=contamination, **params))

                    total_precision.append(precision)
                    total_recall.append(recall)
                    total_f.append(f_score)
                    total_y_pred_count.append(y_pred_count)
                    total_y_true_count.append(y_true_count)

                    logging.info(f'{method}\n'
                                 f'precision: {round(numpy.mean(total_precision), 3)}, {round(numpy.std(total_precision), 3)}\n'
                                 f'recall: {round(numpy.mean(total_recall), 3)}, {round(numpy.std(total_recall), 3)}\n'
                                 f'f: {round(numpy.mean(total_f), 3)}, {round(numpy.std(total_f), 3)}\n')

            except Exception as ex:
                    logging.info(traceback.format_exc())
                    logging.info('Failed with exception, skipping')
                    traceback.print_exc()


def new_id_function(id_mapping, pair):
    return [id_mapping[pair[0]], id_mapping[pair[1]]]


def apply_graph_outlier_detector(transactions, dataset_stats, method):
    additional_columns = (['transaction_count'] if 'transaction_count' in transactions.columns else [])
    edge_features = transactions[['amount'] + additional_columns]
    edge_features = StandardScaler().fit_transform(edge_features)
    edge_attr = torch.tensor(edge_features, dtype=torch.float)
    node_features = dataset_stats[['in_degree', 'out_degree', 'unique_in_degree', 'unique_out_degree', 'in_strength', 'out_strength']]
    node_features = StandardScaler().fit_transform(node_features)
    x = torch.tensor(node_features, dtype=torch.float)
    edge_index = torch.tensor(numpy.array([transactions['origin_id'], transactions['target_id']]), dtype=torch.long)
    num_nodes = len(dataset_stats)
    data = Data(x=x, edge_index=edge_index, num_nodes=num_nodes, edge_attr=edge_attr)
    method.fit(data)
    y_pred = list(map(lambda result: True if result == 1 else False, method.predict()))
    y_true = dataset_stats['is_ml'].to_list()

    precision, recall, f_score, _ = precision_recall_fscore_support(y_true, y_pred, pos_label=True, average='binary')

    y_pred_count = sum(y_pred)
    y_true_count = sum(y_true)

    return precision, recall, y_true_count, y_pred_count, f_score


def main():
    logger_manager.setup_logging()
    benchmark_graph_outlier_detection()


if __name__ == '__main__':
    main()
