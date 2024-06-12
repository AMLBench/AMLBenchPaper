import os.path
import subprocess

import networkx
from networkx.drawing.nx_agraph import to_agraph

from augment import case_transformer
from augment.registry import TransactionKinds, Tasks
from augment.registry.MultiTransaction import MultiTransaction

VISUALIZATION_DIR = 'visualization/cases/'

GRAPH_TRANSACTION_EDGE_COLOR = {
    TransactionKinds.BANK_TRANSFER: 'black',
    TransactionKinds.CASH: 'orange',
    TransactionKinds.DEPOSIT: 'blue',
    TransactionKinds.WITHDRAWAL: 'red',
    TransactionKinds.ASSET: 'purple',
}

GRAPH_NODE_FILL_COLOR = {
    Tasks.SOURCE: 'darkseagreen1',
    Tasks.LAYER: 'white',
    Tasks.DESTINATION: 'mistyrose'
}

def graph_account_edges(person):
    return [(person.identifier, account.identifier,
             {'id': person.identifier,
              'dir': 'none',
              'style': 'dotted',
              'color': 'grey',
              'relationship': 'has_account'
              }) for account in
            person.list_accounts()]


def graph_transaction_edge(transaction):
    amount_representation = str(int(transaction.amount))
    if len(amount_representation) >= 7:
        cut = 6
    elif len(amount_representation) >= 4:
        cut = 3
    else:
        cut = 0

    if cut:
        label = amount_representation[:-cut] + ('K' if cut == 3 else 'M')
        if amount_representation[-cut:] != '0' * cut:
            label = '~' + label
    else:
        label = amount_representation

    if type(transaction) is MultiTransaction and transaction.transaction_count > 1:
        label += ' * ' + str(transaction.transaction_count)
    return transaction.origin.identifier, transaction.target.identifier, {'id': transaction.identifier,
                                                                          'label': label + ' ',
                                                                          'color': GRAPH_TRANSACTION_EDGE_COLOR[transaction.kind],
                                                                          'total_amount': transaction.amount,
                                                                          'relationship': 'sent_money'
                                                                          }


def graph_account_node(account):
    return account.identifier, {'label': account.name, 'type':'account', 'style': 'filled', 'fillcolor': GRAPH_NODE_FILL_COLOR[account.task]}


def visualize_graph(networkx_graph, file_name, cases_source):
    output_dir = VISUALIZATION_DIR + cases_source + '/'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dot_file_path = output_dir + file_name + '.dot'
    png_file_path = output_dir + file_name + '.png'

    viz_graph = to_agraph(networkx_graph)
    viz_graph.edge_attr['fontsize'] = '10px'
    viz_graph.write(dot_file_path)

    command = 'dot  -T png ' + dot_file_path + ' > ' + png_file_path + ';' + 'rm ' + dot_file_path
    import_to_neo4j = subprocess.Popen(command,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=True)
    output, error = import_to_neo4j.communicate()
    output = output.decode('UTF-8 ')
    error = error.decode('UTF-8')
    if output: print(output)
    if error: print(error)


def graph_person_node(person):
    return person.identifier, {'label': person.name, 'shape': 'box', 'style': 'dotted, filled', 'fontcolor': 'grey',
                               'color': 'grey', 'type':'person', 'fillcolor': GRAPH_NODE_FILL_COLOR[person.task]}


def case_to_graph(case, multi_transactions=False):
    graph = networkx.MultiDiGraph()
    graph.add_nodes_from([graph_account_node(account) for account in case.account_registry.list()])

    graph.add_nodes_from([graph_person_node(person) for person in case.person_registry.list()])
    [graph.add_edges_from(graph_account_edges(person)) for person in case.person_registry.list()]

    transactions_data = case.transaction_registry.list()
    if multi_transactions:
        transactions_data = case_transformer.to_multi_transaction(transactions_data)
    graph.add_edges_from([graph_transaction_edge(transaction) for transaction in transactions_data])

    return graph


def validate_graph(graph, case_name):
    def return_transaction_edge(node1, node2):
        edges = graph[node1][node2]
        valid_edges = [edges[i] for i in range(len(edges)) if edges[i]['relationship'] == 'sent_money']
        if valid_edges:
            return valid_edges[0]
        else:
            return None

    number_of_warnings = 0
    for node in graph.nodes():
        sent = 0
        for successor in graph.successors(node):
            edge = return_transaction_edge(node, successor)
            if edge:
                sent += edge['total_amount']
        received = 0
        for predecessor in graph.predecessors(node):
            edge = return_transaction_edge(predecessor, node)
            if edge:
                received += edge['total_amount']
        node_data = graph.nodes(data=True)[node]
        if sent >= received:
            print(f'Warning node {node_data["type"]} {node_data["label"]} from case {case_name} sends {sent} but only receives {received}')
            number_of_warnings += 1
    print(f'Total number of warnings: {number_of_warnings}')