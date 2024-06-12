import os.path
import pandas

from src.augment.registry import TransactionKinds

GENERATE_DATASET_SNAPSHOTS = True

AUGMENT = True
AUGMENT_FRACTIONS = [0.3, 0.6]
AUGMENT_EDGE_WEIGHT_PERTURBATION = 0.05

PARSED_TRANSACTIONS_FILE = 'parsed_transactions.csv'
PARSED_ACCOUNTS_FILE = 'parsed_accounts.csv'

RESULTS_DIR = os.getcwd() + '/results/'
DATASET_SNAPSHOTS_DIR = 'dataset_snapshots/'

AML_SIM_1M_NAME = 'amlsim_1m'
BERKA_PLUS_NAME = 'berka_plus'
RABOBANK_PLUS_NAME = 'rabobank_plus'
ITAML_NAME = 'itaml'

DATA_DIR = os.getcwd() + '/data/'
AML_SIM_1M_DIR = DATA_DIR + 'amlsim/parsed_data/'
RABO_DIR = DATA_DIR + 'rabo/parsed_data/'
BERKA_DIR = DATA_DIR + 'berka/parsed_data/'
ITAML_DIR = DATA_DIR + 'itaml/parsed_data/'

CASES_DIR = DATA_DIR + 'cases/aggregated_transactions/'

class DatasetInfo:
    def __init__(self, name, data_dir, cases_dir):
        self.name = name
        self.data_dir = data_dir
        self.cases_dir = cases_dir

class Dataset:
    def __init__(self, dataset_info):
        self.info = dataset_info
        self.accounts, self.transactions, self.transactions_by_origin, self.transactions_by_target = self.load_dataset()


    def standardize_ids(self, accounts, transactions):
        new_ids = list(range(len(accounts)))
        id_mapping = dict(zip(accounts['account_id'], new_ids))

        transactions['origin_id'] = transactions['origin_id'].map(id_mapping)
        transactions['target_id'] = transactions['target_id'].map(id_mapping)
        accounts['account_id'] = new_ids
        return accounts, transactions

    def multigraph_to_graph(self, transactions):
        return transactions.groupby(['origin_id', 'target_id'], as_index=False).agg(
            amount=pandas.NamedAgg(column="amount", aggfunc="sum"),
            transaction_count=pandas.NamedAgg(column="target_id", aggfunc="count")
        )

    def load_dataset(self):
        default_transaction_cols = ['origin_id', 'target_id', 'amount']

        if self.info.name == AML_SIM_1M_NAME:
            accounts = pandas.read_csv(self.info.data_dir + PARSED_ACCOUNTS_FILE, usecols=['account_id', 'is_ml'])
            transactions = pandas.read_csv(self.info.data_dir + PARSED_TRANSACTIONS_FILE, usecols=default_transaction_cols + ['transaction_count'])

            accounts = self.remove_unused_accounts(accounts, transactions)

        elif self.info.name == ITAML_NAME:
            accounts = pandas.read_csv(self.info.data_dir + PARSED_ACCOUNTS_FILE, usecols=['account_id', 'is_ml'])
            transactions = pandas.read_csv(self.info.data_dir + PARSED_TRANSACTIONS_FILE, usecols=default_transaction_cols + ['is_ml'])

            accounts = self.remove_unused_accounts(accounts, transactions)
            transactions = self.multigraph_to_graph(transactions)

        elif self.info.name == RABOBANK_PLUS_NAME:
            accounts = pandas.read_csv(self.info.data_dir + PARSED_ACCOUNTS_FILE, usecols=['account_id'])
            transactions = pandas.read_csv(self.info.data_dir + PARSED_TRANSACTIONS_FILE,
                                           usecols=default_transaction_cols + ['transaction_count'])

            accounts = self.remove_unused_accounts(accounts, transactions)
            accounts, transactions = self.inject_money_laundering(accounts, transactions, self.info.cases_dir)

        elif self.info.name == BERKA_PLUS_NAME:
            accounts = pandas.read_csv(self.info.data_dir + PARSED_ACCOUNTS_FILE, usecols=['account_id'])
            transactions = pandas.read_csv(self.info.data_dir + PARSED_TRANSACTIONS_FILE, usecols=default_transaction_cols)

            accounts = self.remove_unused_accounts(accounts, transactions)
            accounts, transactions = self.inject_money_laundering(accounts, transactions, self.info.cases_dir)
            transactions = self.multigraph_to_graph(transactions)

        else:
            raise Exception('Dataset loader not implemented for', self.info.name)

        accounts, transactions = self.standardize_ids(accounts, transactions)

        transactions_by_origin = transactions.set_index('origin_id').sort_index()
        transactions_by_target = transactions.set_index('target_id').sort_index()

        if GENERATE_DATASET_SNAPSHOTS:
            print(f'Generating snapshot of {self.info.name} dataset.')
            snapshots_dir = RESULTS_DIR + DATASET_SNAPSHOTS_DIR + self.info.name + '/'
            if not os.path.isdir(snapshots_dir):
                os.mkdir(snapshots_dir)

            accounts.to_csv(snapshots_dir + PARSED_ACCOUNTS_FILE, index=False)
            transactions.to_csv(snapshots_dir + PARSED_TRANSACTIONS_FILE, index=False)

        return accounts, transactions, transactions_by_origin, transactions_by_target

    def remove_unused_accounts(self, accounts, transactions):
        transaction_ids = set(transactions['origin_id']) | set(transactions['target_id'])
        accounts = accounts[accounts['account_id'].isin(transaction_ids)]
        return accounts

    def augment_money_laundering(self, cases_accounts, cases_transactions):
        pandas.options.mode.chained_assignment = None  # default='warn'
        case_ids = cases_accounts['case_id'].unique()

        new_accounts = []
        new_transactions = []

        for case_id in case_ids:
            case_accounts = cases_accounts[cases_accounts['case_id'] == case_id]
            case_transactions = cases_transactions[cases_transactions['case_id'] == case_id]
            for augmentation_id, fraction in enumerate(AUGMENT_FRACTIONS):

                augmented_transactions = case_transactions.sample(frac=(1-fraction), random_state=1)
                augmented_transaction_ids = set(augmented_transactions['origin_id']) | set(augmented_transactions['target_id'])
                augmented_accounts = case_accounts[case_accounts['account_id'].isin(augmented_transaction_ids)]

                id_prefix = f'aug{augmentation_id}_'
                augmented_transactions['transaction_id'] = id_prefix + augmented_transactions['transaction_id']
                augmented_transactions['case_id'] = id_prefix + augmented_transactions['case_id']
                augmented_transactions['origin_id'] = id_prefix + augmented_transactions['origin_id']
                augmented_transactions['target_id'] = id_prefix + augmented_transactions['target_id']

                augmented_accounts['account_id'] = id_prefix + augmented_accounts['account_id']
                augmented_accounts['case_id'] = id_prefix + augmented_accounts['case_id']

                new_transactions.append(augmented_transactions)
                new_accounts.append(augmented_accounts)

        new_transactions_dataframe = pandas.concat([cases_transactions] + new_transactions, ignore_index=True)
        new_accounts_dataframe = pandas.concat([cases_accounts] + new_accounts, ignore_index=True)

        pandas.options.mode.chained_assignment = 'warn'
        return new_accounts_dataframe, new_transactions_dataframe


    def inject_money_laundering(self, accounts, transactions, cases_dir):
        additional_columns = (['transaction_count'] if 'transaction_count' in transactions.columns else [])
        cases_transactions = pandas.read_csv(cases_dir + PARSED_TRANSACTIONS_FILE,
                                             usecols=['transaction_id', 'origin_id', 'target_id', 'amount', 'case_id',
                                                      'kind'] + additional_columns)

        cases_transactions = cases_transactions[cases_transactions['kind'] == TransactionKinds.BANK_TRANSFER]
        cases_accounts = pandas.read_csv(cases_dir + PARSED_ACCOUNTS_FILE, usecols=['account_id', 'case_id'])

        if AUGMENT:
            cases_accounts, cases_transactions = self.augment_money_laundering(cases_accounts, cases_transactions)

        old_ids = cases_accounts['account_id'].to_list()
        injection_accounts = accounts.sample(n=len(old_ids), random_state=1)
        new_ids = injection_accounts['account_id'].to_list()

        cases_transactions[['origin_id', 'target_id']] = cases_transactions[['origin_id', 'target_id']].replace(
            dict(zip(old_ids, new_ids)))

        cases_transactions.insert(len(cases_transactions.columns), 'is_ml', True)

        transactions = pandas.concat([transactions, cases_transactions], ignore_index=True)
        transactions.reset_index()

        accounts.insert(len(accounts.columns), 'is_ml', False)
        accounts.loc[injection_accounts.index, 'is_ml'] = True
        return accounts, transactions

AMLSim1mInfo = DatasetInfo(AML_SIM_1M_NAME, AML_SIM_1M_DIR, CASES_DIR)
BerkaPlusInfo = DatasetInfo(BERKA_PLUS_NAME, BERKA_DIR, CASES_DIR)
RaboPlusInfo = DatasetInfo(RABOBANK_PLUS_NAME, RABO_DIR, CASES_DIR)
ITAmlInfo = DatasetInfo(ITAML_NAME, ITAML_DIR, CASES_DIR)

def get_datasets_info():
    return [AMLSim1mInfo, ITAmlInfo, BerkaPlusInfo, RaboPlusInfo]

def get_datasets():
    datasets = list(map(Dataset, get_datasets_info()))
    return datasets

if __name__ == '__main__':
    get_datasets()