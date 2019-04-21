import json
import os
import random

import config
from datetime import datetime
from time import sleep

from model.xu_model import AgahXuModelRecord, XuModel
from utils.asa import ASAClient
from utils.tse import read_isin_data, get_all_isins

# used for user input
# noinspection PyUnresolvedReferences
from datetime import timedelta


# noinspection PyBroadException
def collect_live_data(interval, duration, directory, *isin_list):

    start_time = datetime.now()
    client = ASAClient(config.ASA_COOKIE)

    while datetime.now() <= start_time + eval(duration):
        for isin in set(isin_list):
            opened_file = open(os.path.join(directory, isin), mode='a+', encoding='utf8')
            try:
                print(client.get_data_from_isin(isin), file=opened_file)
            except:
                print('exception occurred', file=opened_file)
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


def analyze_isin_with_xu_model(file_path, deviation_time):
    deviation_time = eval(deviation_time)
    prediction_time = timedelta(hours=4.5) - deviation_time - timedelta(seconds=0)
    opened_file = open(file_path, encoding='utf8')
    previous_record = None
    records = []
    for line in opened_file:
        line = line.replace('\n', '')
        data = json.loads(line)
        record = AgahXuModelRecord(data, previous_record)
        records.append(record)
        previous_record = record
    XuModel(records).draw(deviation_time=deviation_time, prediction_time=prediction_time)


def sample_xu(directory, count):
    isins = os.listdir(directory)
    r = random.Random()
    for _ in range(int(count)):
        isin = r.choice(isins)
        deviation_time_delta = 'timedelta(hours={})'.format(1 + 2 * r.random())
        analyze_isin_with_xu_model(os.path.join(directory, isin), deviation_time=str(deviation_time_delta))
