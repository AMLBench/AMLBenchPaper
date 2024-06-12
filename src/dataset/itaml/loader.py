import os

from src.dataset.parsing_tools import ColumnNameGenerator
from src.dataset import parsing_tools
from tqdm import tqdm
import pandas

DATASET_DIRECTORY = 'itaml/'
DATABASE_NAME = 'HI-Large_Trans_ach-only'

DATA_DIRECTORY = os.getcwd() + '/data/'
RAW_DATA_DIRECTORY = DATA_DIRECTORY + DATASET_DIRECTORY + 'raw_data/'
PARSED_DATA_DIRECTORY = DATA_DIRECTORY + DATASET_DIRECTORY + 'parsed_data/'

ACCOUNTS_FILE = 'parsed_accounts.csv'
TRANSACTIONS_FILE = 'parsed_transactions.csv'

CONVERSION_RATE = {'US Dollar': 0.8829, 'Euro': 1, 'Yuan': 0.139, 'Shekel': 0.2844, 'UK Pound': 1.1901, 'Canadian Dollar': 0.6948, 'Ruble': 0.0117, 'Yen': 0.0077, 'Australian Dollar': 0.6404, 'Swiss Franc': 0.968, 'Mexican Peso': 0.0432, 'Rupee': 0.0119, 'Brazil Real': 0.1585, 'Saudi Riyal': 0.2354}

NAMES_FOR_TRANSACTION_DATA = \
    [
        ColumnNameGenerator('Timestamp', 'timestamp'),
        ColumnNameGenerator('Account', 'origin_id'),
        ColumnNameGenerator('Account.1', 'target_id'),
        ColumnNameGenerator('Amount Paid', 'amount'),
        ColumnNameGenerator('Is Laundering', 'is_ml'),
    ]


def parse_transaction_data():
    transactions = pandas.read_csv(RAW_DATA_DIRECTORY + 'HI-Large_Trans_ach-only.csv')
    transactions = transactions[['Timestamp', 'Account', 'Account.1', 'Amount Paid', 'Payment Currency', 'Is Laundering']]
    transactions['Amount Paid'] = transactions['Payment Currency'].map(CONVERSION_RATE) * transactions['Amount Paid']
    transactions.drop(columns=['Payment Currency'], inplace=True)
    ml_transactions = transactions[transactions['Is Laundering'] == 1]
    ml_accounts = set(ml_transactions['Account']) | set(ml_transactions['Account.1'])
    all_accounts = set(transactions['Account']) | set(transactions['Account.1'])
    non_ml_accounts = all_accounts - ml_accounts
    accounts = pandas.DataFrame({'account_id': list(non_ml_accounts) + list(ml_accounts), 'is_ml': [False] * len(non_ml_accounts) + [True] * len(ml_accounts)})
    transactions['Is Laundering'] = transactions['Is Laundering'].map({1: True, 0: False})
    return accounts, transactions

def save_to_csv(parsed_accounts, parsed_transactions):
    parsed_accounts.to_csv(PARSED_DATA_DIRECTORY + ACCOUNTS_FILE, index=False)

    parsed_transactions. \
        rename(columns=parsing_tools.get_csv_name_map(NAMES_FOR_TRANSACTION_DATA)). \
        to_csv(PARSED_DATA_DIRECTORY + TRANSACTIONS_FILE, index=False)



def main():
    tqdm.pandas()
    print('Parsing transaction data')
    parsed_accounts, parsed_transactions = parse_transaction_data()
    print('Saving data to CSV')
    save_to_csv(parsed_accounts, parsed_transactions)

if __name__ == '__main__':
    main()
