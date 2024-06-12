import wget

from src.dataset.parsing_tools import ColumnNameGenerator
from src.dataset import parsing_tools
from tqdm import tqdm
import pandas

ZIP_FILE = 'dataset.7z'

DATASET_DIRECTORY = 'amlsim/'
DATABASE_NAME = '1m_dataset'

DATA_DIRECTORY = 'data/'
RAW_DATA_DIRECTORY = DATA_DIRECTORY + DATASET_DIRECTORY + 'raw_data/'
PARSED_DATA_DIRECTORY = DATA_DIRECTORY + DATASET_DIRECTORY + 'parsed_data/'

ACCOUNTS_FILE = 'parsed_accounts.csv'
TRANSACTIONS_FILE = 'parsed_transactions.csv'

NAMES_FOR_ACCOUNT_DATA = \
    [
        ColumnNameGenerator('ACCOUNT_ID', 'account_id'),
        ColumnNameGenerator('IS_FRAUD', 'is_ml')
    ]

NAMES_FOR_TRANSACTION_DATA = \
    [
        ColumnNameGenerator('SENDER_ACCOUNT_ID', 'origin_id'),
        ColumnNameGenerator('RECEIVER_ACCOUNT_ID', 'target_id'),
    ]

def parse_account_data():
    accounts = pandas.read_csv(RAW_DATA_DIRECTORY + 'accounts.csv', usecols=['ACCOUNT_ID', 'IS_FRAUD'])
    return accounts
    

def parse_transaction_data():
    transactions = pandas.read_csv(RAW_DATA_DIRECTORY + 'transactions_minimal.csv', usecols=['SENDER_ACCOUNT_ID', 'RECEIVER_ACCOUNT_ID', 'TX_AMOUNT'])
    transactions = transactions.groupby(['SENDER_ACCOUNT_ID', 'RECEIVER_ACCOUNT_ID'], as_index=False).agg(
            amount=pandas.NamedAgg(column="TX_AMOUNT", aggfunc="sum"),
            transaction_count=pandas.NamedAgg(column="RECEIVER_ACCOUNT_ID", aggfunc="count")
    )
    return transactions


def save_to_csv(parsed_accounts, parsed_transactions):
    parsed_accounts. \
        rename(columns=parsing_tools.get_csv_name_map(NAMES_FOR_ACCOUNT_DATA)). \
        to_csv(PARSED_DATA_DIRECTORY + ACCOUNTS_FILE, index=False)

    parsed_transactions. \
        rename(columns=parsing_tools.get_csv_name_map(NAMES_FOR_TRANSACTION_DATA)). \
        to_csv(PARSED_DATA_DIRECTORY + TRANSACTIONS_FILE, index=False)

def main():
    tqdm.pandas()
    print('Parsing account data')
    parsed_accounts = parse_account_data()
    print('Parsing transaction data')
    parsed_transactions = parse_transaction_data()
    print('Saving data to CSV')
    save_to_csv(parsed_accounts, parsed_transactions)

if __name__ == '__main__':
    main()
