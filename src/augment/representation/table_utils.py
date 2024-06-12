from collections import defaultdict

import pandas

from augment import case_transformer

OUTPUT_DATA_DIRECTORY_SINGLE_TRANSACTION = './data/cases_single_transaction/parsed_data/'
OUTPUT_DATA_DIRECTORY_MULTI_TRANSACTION = './data/cases_multi_transaction/parsed_data/'
PERSONS_FILE = 'parsed_persons.csv'
ACCOUNTS_FILE = 'parsed_accounts.csv'
ACCOUNTS_PER_PERSON_FILE = 'parsed_accounts_per_person.csv'
TRANSACTIONS_FILE = 'parsed_transactions.csv'

def table_person_registry(person_registry, case_id):
    data = defaultdict(list)
    for person in person_registry:
        data['account_id'] = person.identifier
        data['account_name'] = person.name
        data['case_id'] = case_id
    return data

def cases_to_table(case_registry, multi_transactions=False):
    persons = []
    accounts_per_person = []
    accounts = []
    transactions = []
    for case in case_registry.list():
        case_information = [case.identifier, case.name, case.source]

        for person in case.person_registry.list():
            persons.append([person.identifier, person.name, person.task] + case_information)
            for account in person.list_accounts():
                accounts_per_person.append([person.identifier, account.identifier])

        for account in case.account_registry.list():
            accounts.append([account.identifier, account.name, account.task] + case_information)

        if multi_transactions:
            transactions_data = case_transformer.to_multi_transaction(case.transaction_registry.list())
            multi_transactions_header = ['transaction_count']
        else:
            transactions_data = case.transaction_registry.list()
            multi_transactions_header = []

        for transaction in transactions_data:
            multi_transaction_data = [transaction.transaction_count] if multi_transactions else []
            transactions.append([transaction.identifier, transaction.origin.identifier, transaction.target.identifier, transaction.amount] + multi_transaction_data + [transaction.kind] + case_information)

        data_directory = OUTPUT_DATA_DIRECTORY_SINGLE_TRANSACTION if not multi_transactions else OUTPUT_DATA_DIRECTORY_MULTI_TRANSACTION
        case_information_header = ['case_id', 'case_name', 'case_source']
        pandas.DataFrame(data=persons, columns=['entity_id', 'name', 'task'] + case_information_header).to_csv(data_directory + PERSONS_FILE, index=False)
        pandas.DataFrame(data=accounts_per_person, columns=['account_id', 'person_id']).to_csv(data_directory + ACCOUNTS_PER_PERSON_FILE, index=False)
        pandas.DataFrame(data=accounts, columns=['account_id', 'name', 'task'] + case_information_header).to_csv(data_directory + ACCOUNTS_FILE, index=False)
        pandas.DataFrame(data=transactions, columns=['transaction_id', 'origin_id', 'target_id', 'amount'] + multi_transactions_header + ['kind'] + case_information_header).to_csv(data_directory + TRANSACTIONS_FILE, index=False)