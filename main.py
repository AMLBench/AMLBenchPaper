import os

import pandas

from src.experiments.benchmark import benchmark
from src.dataset import load_data
from src.experiments.timestamp_analysis import analyze_timestamps
from src.experiments import dataset_stats
from src.experiments import dataset_stats_visualizer
from src.tools import setup

def main():
    setup.main()
    print('Loading data')
    load_data.main()
    print('Analyzing timestamps')
    analyze_timestamps.main()
    print('Generating dataset stats')
    dataset_stats.main()
    print('Creating visualizations for dataset stats')
    dataset_stats_visualizer.main()
    print('Benchmarking')
    benchmark.main()


if __name__ == '__main__':
    main()
