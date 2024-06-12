import os

import pandas
import matplotlib.pyplot as plt
from tqdm import tqdm

N_SAMPLES = 10

def main():
    data = pandas.read_csv(os.getcwd() + '/data/amlsim/raw_data/transactions.csv', usecols=['TIMESTAMP', 'SENDER_ACCOUNT_ID', 'RECEIVER_ACCOUNT_ID'])
    accounts = pandas.read_csv(os.getcwd() + '/data/amlsim/raw_data/accounts.csv')['ACCOUNT_ID']
    for account in tqdm(accounts.sample(N_SAMPLES)):
        plt.figure(figsize=(2, 2))
        plt.title(f'account {account}', fontsize=10)
        y, x, _ = plt.hist(data[data['SENDER_ACCOUNT_ID'] == account]['TIMESTAMP'].values, density=False, bins=range(200))
        plt.xticks([0, 99, 199], labels=[1, 100, 200])
        plt.yticks([0, max(y)], labels=[0, round(max(y))])
        plt.ylim(0, max(y) + 1)
        plt.savefig(f'results/timestamps/amlsim/send_{account}.png')
        plt.cla()


if __name__ == '__main__':
    main()
