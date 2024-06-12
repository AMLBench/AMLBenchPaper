from collections import defaultdict

from augment.registry.IdGenerator import IdGenerator
from augment.registry.MultiTransaction import MultiTransaction


def to_multi_transaction(transaction_list):
    id_generator = IdGenerator('mt', 0)
    transaction_dict = defaultdict(list)
    for transaction in transaction_list:
        origin_identifier = transaction.origin.identifier
        target_identifier = transaction.target.identifier
        kind = transaction.kind
        transaction_dict[(origin_identifier, target_identifier, kind)].append(transaction)


    return [MultiTransaction(id_generator.new_id(), transactions) for transactions in transaction_dict.values()]

