import os
import re

import matplotlib.pyplot as plt
import pandas

from src.experiments import datasets

DATASET_STATS_VISUALIZATION_DIR = os.getcwd() + '/results/dataset_stats_visualization/'
DATASET_STATS_RESULTS_DIR = os.getcwd() + '/results/dataset_stats/'

def draw_scatter_plot(x, y, x_label, y_label, title, log1=False, log2=False, color='blue', mini_fig_data=None):
    plt.rc('font', weight='bold', family='Arial', size='60')

    log1_label = ' (log)' if log1 else ''
    log2_label = ' (log)' if log2 else ''

    fig, ax = plt.subplots(figsize=(20, 20))
    fig.set_tight_layout(True)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.setp(ax.spines.values(), linewidth=5)

    plt.xlabel(x_label + log1_label, fontsize=60, labelpad=40, weight='bold', family='Arial')
    plt.ylabel(y_label + log2_label, fontsize=60, labelpad=40, weight='bold', family='Arial')

    ax.tick_params(axis='both', which='major', width=4, length=12)

    plt.scatter(x, y, c=color)

    plt.ticklabel_format(style='plain')
    # plt.title(title, fontsize=40)

    if log1:
        ax.set_xscale("log")
    if log2:
        ax.set_yscale("log")

    if mini_fig_data:
        sub_ax = fig.add_axes([0.82, 0.82, 0.16, 0.16])
        sub_ax.set_xlim(ax.get_xlim())
        sub_ax.set_ylim(ax.get_ylim())
        sub_ax.get_xaxis().set_visible(False)
        sub_ax.get_yaxis().set_visible(False)
        sub_ax.scatter(*mini_fig_data, c='red', s=2)
        plt.setp(sub_ax.spines.values(), linewidth=2)
        if log1:
            sub_ax.set_xscale("log")
        if log2:
            sub_ax.set_yscale("log")

    plt.savefig(DATASET_STATS_VISUALIZATION_DIR + re.sub(' ', '_', title) + '.png')

def draw_line_plot(x_ticks, y, x_label, y_label, title, log=False):
    log_label = 'log_' if log else ''

    fig, ax = plt.subplots(figsize=(20, 20))
    plt.xlabel(x_label, fontsize=45)
    plt.ylabel(log_label + y_label, fontsize=45)

    ax.tick_params(axis='both', which='major', labelsize=30)
    ax.set_xticks(x_ticks)

    plt.plot(y, c='blue')

    plt.ticklabel_format(style='plain')
    if log:
        ax.set_yscale("log")

    plt.savefig(DATASET_STATS_VISUALIZATION_DIR + re.sub(' ', '_', title) + '.png')


def main():
    for dataset_info in datasets.get_datasets_info():
        dataset_stats = pandas.read_csv(DATASET_STATS_RESULTS_DIR + dataset_info.name + '_stats.csv').sample(frac=1)
        dataset_stats = dataset_stats.sort_values(by='is_ml', ascending=False)
        ml_stats = dataset_stats[dataset_stats['is_ml']]

        scatter_plot_color = dataset_stats['is_ml'].map({True: '#D60A1A', False: '#2596BE'})
        draw_scatter_plot(dataset_stats['in_degree'], dataset_stats['out_degree'], 'No. of transfers received',
                          'No. of transfers sent',
                          dataset_info.name + ' number of transfers per account', log1=True, log2=True,
                          color=scatter_plot_color,
                          mini_fig_data=(ml_stats['in_degree'], ml_stats['out_degree']))

        draw_scatter_plot(dataset_stats['unique_in_degree'], dataset_stats['unique_out_degree'],
                          'No. of accounts received money from',
                          'No. of accounts sent money to',
                          dataset_info.name + ' number of accounts transacted with per account', log1=True, log2=True,
                          color=scatter_plot_color,
                          mini_fig_data=(ml_stats['unique_in_degree'], ml_stats['unique_out_degree']))

        draw_scatter_plot(dataset_stats['in_strength'], dataset_stats['out_strength'], 'Total money received',
                          'Total money sent',
                          dataset_info.name + ' amounts transferred per account', log1=True, log2=True,
                          color=scatter_plot_color,
                          mini_fig_data=(ml_stats['in_strength'], ml_stats['out_strength']))


if __name__ == '__main__':
    main()