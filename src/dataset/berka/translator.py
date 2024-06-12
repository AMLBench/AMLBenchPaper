OPERATION_TRANSLATION = {'VKLAD': 'deposit',
                         'VYBER': 'withdrawal',
                         'VYBER KARTOU': 'card_payment',
                         'PREVOD Z UCTU': 'transaction_received',
                         'PREVOD NA UCET': 'transaction_sent'}

TYPE_TRANSLATION = {'VYDAJ': 'expense', 'PRIJEM': 'income', 'VYBER': '?'}


def translate_transaction_data(transaction_data):
    if 'operation' in transaction_data.columns:
        transaction_data['operation'] = transaction_data['operation'].map(OPERATION_TRANSLATION)
    if 'type' in transaction_data.columns:
        transaction_data['type'] = transaction_data['type'].map(TYPE_TRANSLATION)
    return transaction_data


def czech_koruna_to_us_dollar(czech_koruna):
    return czech_koruna * 0.047
