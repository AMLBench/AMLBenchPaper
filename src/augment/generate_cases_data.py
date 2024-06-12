import itertools
import os
import importlib
import random

from augment.registry.CaseRegistry import CaseRegistry
from augment.registry.IdGenerator import IdGenerator
from augment.representation import table_utils, graph_utils

CASES_DIR = 'src/augment/case_builders/'

def main():
    random.seed(1)
    cases_sources = [source for source in os.listdir(CASES_DIR) if (source != '__pycache__') and (source != 'backup')]

    case_registry = CaseRegistry(IdGenerator('c', 0))
    for cases_source in cases_sources:
        for case_builder in [importlib.import_module('case_builders.' + cases_source + '.' + file[:-3]) for file in os.listdir(CASES_DIR + cases_source + '/') if file[-3:] == '.py']:
            case = case_registry.new_case(case_builder)
            graph = graph_utils.case_to_graph(case, multi_transactions=True)
            graph_utils.visualize_graph(graph, case.name, case.source)

    table_utils.cases_to_table(case_registry, multi_transactions=True)
    table_utils.cases_to_table(case_registry, multi_transactions=False)

    print('nr. of cases: ', case_registry.get_cases_count())
    print('nr. of persons added:', case_registry.get_person_count())
    print('nr. of accounts added:', case_registry.get_account_count())
    print('nr. of transactions added:', case_registry.get_transaction_count())


if __name__ == '__main__':
    main()