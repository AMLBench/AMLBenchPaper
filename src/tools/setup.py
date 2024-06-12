import os

REQUIRED_DIRECTORIES = [
    '/data/rabo/parsed_data',
    '/data/itaml/parsed_data',
    '/data/berka/parsed_data',
    '/data/amlsim/parsed_data',
    '/log',
    '/results/timestamps/itaml',
    '/results/timestamps/amlsim',
    '/results/dataset_stats_visualization',
    '/results/dataset_stats',
    '/results/dataset_snapshots',
    '/results/dataset_snapshots/amlsim_1m',
    '/results/dataset_snapshots/itaml',
    '/results/dataset_snapshots/berka_plus',
    '/results/dataset_snapshots/rabobank_plus'
]


def main():
    for directory in REQUIRED_DIRECTORIES:
        os.makedirs(os.getcwd() + directory, exist_ok=True)
