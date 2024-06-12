from src.experiments.benchmark import benchmark_supervised_learning
from src.experiments.benchmark import benchmark_generic_outlier_detection
from src.experiments.benchmark import benchmark_graph_outlier_detection


def main():
    print('Benchmarking supervised learning methods')
    benchmark_supervised_learning.main()
    print('Benchmarking general outlier detection methods')
    benchmark_generic_outlier_detection.main()
    print('Benchmarking graph outlier detection methods')
    benchmark_graph_outlier_detection.main()


if __name__ == '__main__':
    main()
