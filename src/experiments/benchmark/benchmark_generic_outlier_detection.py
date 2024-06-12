import os
import numpy
import tqdm
import pandas
from sklearn.metrics import precision_recall_fscore_support
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from src.experiments import datasets
import logging
import src.tools.logger_manager
from src.experiments.datasets import AML_SIM_1M_NAME, RABOBANK_PLUS_NAME, ITAML_NAME, BERKA_PLUS_NAME

PARSED_TRANSACTIONS_FILE = 'parsed_transactions.csv'
PARSED_ACCOUNTS_FILE = 'parsed_accounts.csv'

DATASET_STATS_RESULTS_DIR = os.getcwd() + '/results/dataset_stats/'

N_RUNS = 5
def benchmark_generic_outlier_detection():
    for dataset_info in datasets.get_datasets_info():
        dataset_stats = pandas.read_csv(DATASET_STATS_RESULTS_DIR + dataset_info.name + '_stats.csv').sample(frac=1)
        dataset_features = StandardScaler().fit_transform(dataset_stats[['in_degree', 'out_degree', 'unique_in_degree', 'unique_out_degree', 'in_strength', 'out_strength']])

        for algorithm_name, algorithm in zip(['IF', 'LOF', 'OC SVM'],
                                             [IsolationForest(), LocalOutlierFactor(), OneClassSVM()]):

            if dataset_info.name in [ITAML_NAME, AML_SIM_1M_NAME, RABOBANK_PLUS_NAME] and algorithm_name == 'OC SVM':
                continue

            total_precision = []
            total_recall = []
            total_f = []
            total_y_pred_count = []
            total_y_true_count = []
            for _ in tqdm.tqdm(range(N_RUNS)):

                logging.info(f'Applying {algorithm_name} to {dataset_info.name}')

                y_pred = list(map(lambda result: True if result == -1 else False, algorithm.fit_predict(dataset_features)))

                y_true = dataset_stats['is_ml'].to_list()

                precision, recall, f_score, _ = precision_recall_fscore_support(y_true, y_pred, pos_label=True, average='binary')

                y_true_count = sum(y_true)
                y_pred_count = sum(y_pred)

                total_precision.append(precision)
                total_recall.append(recall)
                total_f.append(f_score)
                total_y_pred_count.append(y_pred_count)
                total_y_true_count.append(y_true_count)

            logging.info(f'{algorithm_name}\n'
                         f'precision: {round(numpy.mean(total_precision), 3)}, {round(numpy.std(total_precision), 3)}\n'
                         f'recall: {round(numpy.mean(total_recall), 3)}, {round(numpy.std(total_recall), 3)}\n'
                         f'f: {round(numpy.mean(total_f), 3)}, {round(numpy.std(total_f), 3)}\n')


def main():
    src.tools.logger_manager.setup_logging()
    benchmark_generic_outlier_detection()

if __name__ == '__main__':
    main()