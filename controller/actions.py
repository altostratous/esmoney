import os

import config
from datetime import datetime
from time import sleep
from utils.asa import ASAClient
from utils.tse import read_isin_data, get_all_isins

# used for user input
# noinspection PyUnresolvedReferences
from datetime import timedelta


def collect_live_data(interval, duration, directory, *isin_list):

    start_time = datetime.now()
    client = ASAClient(config.ASA_COOKIE)

    while datetime.now() <= start_time + eval(duration):
        for isin in set(isin_list):
            opened_file = open(os.path.join(directory, isin), mode='a+', encoding='utf8')
            print(client.get_data_from_isin(isin), file=opened_file)
            opened_file.close()
        sleep(eval(interval))


def find_most_significant_isins(start_date, count):

    all_isins = get_all_isins()

    aggregated_data = []

    for isin in all_isins:
        volume_sum = 0
        for day_data in read_isin_data(isin):
            if day_data[0] < start_date:
                continue
            volume_sum += int(day_data[6])
        aggregated_data.append((volume_sum, isin))

    print(*[isin_tuple[1] for isin_tuple in (list(reversed(sorted(aggregated_data)))[0:eval(count)])])
