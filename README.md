## Data
Money laundering case data can be found in `/data/cases/individual_transactions/`
- The *parsed_account.csv* file contains information relative to each bank account involved in money laundering. It has the following columns:
  - account_id: a unique identifier for the account.
  - name: the name of the account associated with the money laundering case.
  - case_id: a unique identifier for the money laundering case associated with the account.
  - case_name: the name of the money laundering case associated with the account.
  - case_source: the source from which the money laundering case was extracted (more information regarding each case can be found in the paper).

- The *parsed_transactions.csv* file contains information relative to each money laundering transaction. It has the following columns:
  - transaction_id: a unique identifier for the transaction.
  - origin_id: the account id of the sender of the transaction.
  - target_id: the account id of the receiver of the transaction.
  - amount: the amount involved in the transaction in euros
  - case_id: a unique identifier for the money laundering case associated with the transaction.
  - case_name: the name of the money laundering case associated with the transaction.
  - case_source: the source from which the money laundering case was extracted (more information regarding each case can be found in the paper).


## Executing experiments
### Step 1, setup Python environment (tested on Python 3.11):
```
git clone https://github.com/AMLBench/AMLBenchPaper
cd AMLBenchPaper
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### Step 2, download the datasets:
- Rabobank
  - Acquire dataset from https://github.com/akratiiet/RaboBank_Dataset/blob/main/README.md
  - Move the *.csv* provided with transaction data to `/data/rabo/raw_data/` and rename the file *rabo.csv*
- Berka 
  - Dataset is included with this repository. No action needed.
- AMLSim
  - Download 1Mvertices-100Medges dataset from https://github.com/IBM/AMLSim/wiki/Download-Example-Data-Set#1m-100m-1m-accounts-100m-transactions
  - Extract .7z
  - Move *transactions.csv* and *accounts.csv* to `/data/amlsim/raw_data/`
- AMLworld / ITAML
  - Download HI-Large_Patterns.txt from https://kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml/data
  - Move *HI-Large_Patterns.txt* to `/data/itaml/raw_data/`
  - Rename *HI-Large_Patterns.txt* to *HI-Large_Patterns.csv*

### Step 3, run the code:
On the root directory of the project run `python main.py`

### Step 4, interpret the results:
- In directory `/log/` you can find the results of the benchmarking experiments.
- In directory `/results/dataset_snapshops/` you can find the datasets used in the experiments after money laundering injection and preprocessing.
- In directory `/results/dataset_stats/` you can find the features used in the experiments for each bank account.
- In directory `/results/dataset_stats_visualization/` you can find the scatterplots used in the paper
- In directory `/results/timestamps` you can find the timestamp plots used in the paper

### Notes
- In this repository IT-AML refers to the AMLworld dataset. The name comes from the Arxiv pre-print.
- In this repository RabobankPlus refers to the dataset generated using AMLBench by combining case data with the Rabobank dataset.
- In this repository BerkaPlus refers to the dataset generated using AMLBench by combining case data with the Berka dataset.