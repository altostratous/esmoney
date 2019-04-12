import csv
import config
import os


def read_isin_data(isin):

    tse_file = open(os.path.join(config.TSE_DATA_PATH, isin + '.csv'), encoding='utf-16')
    tse_reader = csv.reader(tse_file)

    for row in tse_reader:
        if '<LOW>' in row:
            continue
        yield row


def get_all_isins():
    for file_name in os.listdir(config.TSE_DATA_PATH):
        yield file_name.split('.')[0]
