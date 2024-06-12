import os

import numpy
import pandas
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.experiments import datasets
import logging
import src.tools.logger_manager
import xgboost

PARSED_TRANSACTIONS_FILE = 'parsed_transactions.csv'
PARSED_ACCOUNTS_FILE = 'parsed_accounts.csv'

DATASET_STATS_RESULTS_DIR = os.getcwd() + '/results/dataset_stats/'

N_RUNS = 5
def benchmark_supervised_learning():
    for dataset_info in datasets.get_datasets_info():
        dataset_stats = pandas.read_csv(DATASET_STATS_RESULTS_DIR + dataset_info.name + '_stats.csv').sample(frac=1)
        dataset_features = StandardScaler().fit_transform(dataset_stats[['in_degree', 'out_degree', 'unique_in_degree',
                                                                         'unique_out_degree', 'in_strength',
                                                                         'out_strength']])
        labels = dataset_stats['is_ml']

        for algorithm_name, algorithm in zip(['NB', 'SVM', 'XGBoost'],
                                             [GaussianNB(), SVC(), xgboost.XGBClassifier()]):

            if algorithm_name == 'SVM' and dataset_info.name != datasets.BERKA_PLUS_NAME:
                continue

            total_precision = []
            total_recall = []
            total_f = []
            total_y_pred_count = []
            total_y_true_count = []

            for _ in range(N_RUNS):
                x_train, x_test, y_train, y_test = train_test_split(dataset_features, labels, stratify=labels,
                                                                    test_size=0.30)
                logging.info(f'Applying {algorithm_name} to {dataset_info.name}')

                algorithm.fit(x_train, y_train)
                y_pred = algorithm.predict(x_test)

                precision, recall, f_score, _ = precision_recall_fscore_support(y_test, y_pred, pos_label=True,
                                                                                average='binary')

                y_true_count = sum(y_test)
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
    benchmark_supervised_learning()

if __name__ == '__main__':
    main()