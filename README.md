# CRU data parser

This code will parse CRU data into a SQLite database with the following format, which is then a bit easier to work with and pull statistics from.

| Xref | Yref | Date     | Value |
| :--- | :--- | :------- | :---- |
| 1    | 148  | 1/1/1991 | 3020  |
| 1    | 148  | 2/1/1991 | 2820  |
| ...  | ...  | ...      | ...   |

Details of the data can be found on the [CRU data](https://crudata.uea.ac.uk/~timm/grid/CRU_TS_2_1.html) homepage.  

## Python environment

The code is designed to run in Python 3.x.  One additional module is required, "[Logzero](https://logzero.readthedocs.io/en/latest)", which is shown in the requirements.txt.  If you wish to create a Python environment for the code you can do that by following the commands below, assuming you are using [Anaconda](https://www.anaconda.com/).

```
conda create -n cru python=3.8
conda activate cru
conda install -r requirements.txt
```

## Running the code

The code has two required parameters:

- "cru_file" - CRU input file
- "db_file" - SQLite output database file

To execute the code you would type something along the lines of:

```
cru.py --cru_file cru_ts_2_10.1991-2000_cutdown.pre --db_file cru.sqlite
```

