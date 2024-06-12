import os

import pandas
import matplotlib.pyplot as plt
from tqdm import tqdm

N_SAMPLES = 10

def main():
    data = pandas.read_csv(os.getcwd() + '/data/itaml/raw_data/HI-Large_Trans_ach-only.csv', usecols=['Timestamp', 'Account', 'Account.1', 'Is Laundering', 'Payment Format'])
    data['Timestamp'] = data['Timestamp'].apply(lambda t: t.split(' ')[0])
    data['ParsedTime'] = pandas.to_datetime(data['Timestamp'].apply(lambda t: t.split(' ')[0]), format='%Y/%m/%d')
    data = data.sort_values(by='ParsedTime')
    date_conversion_dict = {date: i for i, date in enumerate(data['Timestamp'].unique())}
    data['Timestamp'] = data['Timestamp'].map(date_conversion_dict)

    for account in tqdm(data['Account'].sample(N_SAMPLES)):
        plt.figure(figsize=(2, 2))
        plt.title(f'account {account}', fontsize=10)
        y, x, _ = plt.hist(data[data['Account'] == account]['Timestamp'].values, density=False, bins=range(165))
        plt.xticks([0, 83, 164], labels=[1, 84, 165])
        plt.yticks([0, max(y)], labels=[0, round(max(y))])
        plt.ylim(0, max(y) + 1)
        plt.savefig(f'results/timestamps/itaml/send_{account}.png')
        plt.cla()


if __name__ == '__main__':
    main()


