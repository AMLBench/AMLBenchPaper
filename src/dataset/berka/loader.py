import tarfile

import wget

from src.dataset import parsing_tools
from src.dataset.berka import translator
from src.dataset.parsing_tools import ColumnNameGenerator
import os
import pandas
from tqdm import tqdm

DATASET_DIRECTORY = 'berka/'
DATABASE_NAME = 'berka'

DATA_DIRECTORY = os.getcwd() + '/data/'
RAW_DATA_DIRECTORY = DATA_DIRECTORY + DATASET_DIRECTORY + 'raw_data/'
PARSED_DATA_DIRECTORY = DATA_DIRECTORY + DATASET_DIRECTORY + 'parsed_data/'

ZIP_FILE = 'dataset.7z'

ACCOUNTS_FILE = 'parsed_accounts.csv'
TRANSACTIONS_FILE = 'parsed_transactions.csv'
OWNERS_FILE = 'parsed_owners.csv'
CLIENTS_FILE = 'parsed_clients.csv'

NAMES_FOR_DATA = [
    ColumnNameGenerator('account_id', neo4j_type='ID'),
    ColumnNameGenerator('client_id', neo4j_type='ID'),
    ColumnNameGenerator('disp_id', 'owner_id'),
    ColumnNameGenerator('trans_id', 'transaction_id'),
    ColumnNameGenerator('origin_id', neo4j_type='START_ID'),
    ColumnNameGenerator('target_id', neo4j_type='END_ID'),
    ColumnNameGenerator('date', 'timestamp')
]

def parse_account_ids_column(dataset):
    dataset['account_id'] = dataset['account_id'].apply(lambda account_id: f'a{account_id}')

def parse_account_column(dataset):
    dataset['account'] = dataset['account'].apply(lambda account_id: f'a{account_id}')

def parse_client_ids_column(dataset):
    dataset['client_id'] = dataset['client_id'].apply(lambda client_id: f'c{client_id}')


def parse_owner_ids_column(dataset):
    dataset['disp_id'] = dataset['disp_id'].apply(lambda relation_id: f'ca{relation_id}')


def parse_transaction_ids_column(dataset):
    dataset['trans_id'] = dataset['trans_id'].apply(lambda relation_id: f't{relation_id}')


def parse_client_data():
    dataset = pandas.read_csv(RAW_DATA_DIRECTORY + 'client.asc', sep=';', usecols=['client_id'])
    dataset['client_id'] = dataset['client_id'].apply(lambda client_id: f'c{client_id}')
    return dataset


def parse_account_data():
    internal_accounts = set(pandas.read_csv(RAW_DATA_DIRECTORY + 'account.asc', sep=';', usecols=['account_id'])['account_id'])
    transactions = pandas.read_csv(RAW_DATA_DIRECTORY + 'trans.asc', sep=';', usecols=['account'])
    external_accounts = set(transactions[~transactions['account'].isna() & (transactions['account'] != 0)]['account'].astype(int))
    accounts = pandas.DataFrame({'account_id': list(internal_accounts | external_accounts)})
    parse_account_ids_column(accounts)
    return accounts


def parse_owner_data():
    dataset = pandas.read_csv(RAW_DATA_DIRECTORY + 'disp.asc', sep=';', usecols=['disp_id', 'client_id', 'account_id'])
    parse_account_ids_column(dataset)
    parse_client_ids_column(dataset)
    parse_owner_ids_column(dataset)
    return dataset

def parse_transaction_record(transaction):
    accounts = (transaction['account_id'], transaction['account']) if transaction['operation'] == 'transaction_sent' else (transaction['account'], transaction['account_id'])
    column_names = ['trans_id', 'origin_id', 'target_id', 'timestamp', 'amount']
    data = [transaction['trans_id'], *accounts, transaction['date'], translator.czech_koruna_to_us_dollar(transaction['amount'])]
    return pandas.Series(dict(zip(column_names, data)))
def parse_transaction_data():
    dataset = pandas.read_csv(RAW_DATA_DIRECTORY + 'trans.asc', sep=';',
                              usecols=['trans_id', 'account_id', 'date', 'operation', 'amount', 'account'], dtype={'account': 'Int64'})
    dataset = dataset.drop(304834) #incomplete data (transaction without receiver id)
    translator.translate_transaction_data(dataset)
    dataset = dataset[(dataset['operation'] == 'transaction_sent') | (dataset['operation'] == 'transaction_received')]
    parse_account_column(dataset)
    parse_account_ids_column(dataset)
    parse_transaction_ids_column(dataset)
    dataset = dataset.progress_apply(parse_transaction_record, axis=1)
    return dataset


def save_to_csv(parsed_accounts, parsed_transactions, parsed_owners, parsed_clients):
    account_data_names = {x for x in NAMES_FOR_DATA if x.old_name in parsed_accounts.columns}
    transactions_data_names = {x for x in NAMES_FOR_DATA if x.old_name in parsed_transactions.columns}
    owners_data_names = {x for x in NAMES_FOR_DATA if x.old_name in parsed_owners.columns}
    clients_data_names = {x for x in NAMES_FOR_DATA if x.old_name in parsed_clients.columns}

    parsed_accounts. \
        rename(columns=parsing_tools.get_csv_name_map(account_data_names)). \
        to_csv(PARSED_DATA_DIRECTORY + ACCOUNTS_FILE, index=False)
    parsed_transactions. \
        rename(columns=parsing_tools.get_csv_name_map(transactions_data_names)). \
        to_csv(PARSED_DATA_DIRECTORY + TRANSACTIONS_FILE, index=False)
    parsed_owners. \
        rename(columns=parsing_tools.get_csv_name_map(owners_data_names)). \
        to_csv(PARSED_DATA_DIRECTORY + OWNERS_FILE, index=False)
    parsed_clients. \
        rename(columns=parsing_tools.get_csv_name_map(clients_data_names)). \
        to_csv(PARSED_DATA_DIRECTORY + CLIENTS_FILE, index=False)


def main():
    tqdm.pandas()
    print('Parsing account data')
    parsed_accounts = parse_account_data()
    print('Parsing transaction data')
    parsed_transactions = parse_transaction_data()
    print('Parsing client data')
    parsed_clients = parse_client_data()
    print('Parsing owner data')
    parsed_owners = parse_owner_data()

    print('Saving data to CSV')
    save_to_csv(
        parsed_accounts=parsed_accounts,
        parsed_transactions=parsed_transactions,
        parsed_clients=parsed_clients,
        parsed_owners=parsed_owners
    )

if __name__ == '__main__':
    main()
