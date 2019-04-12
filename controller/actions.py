import os

import config
from datetime import datetime
from time import sleep
from utils.asa import ASAClient

# used for user input
# noinspection PyUnresolvedReferences
from datetime import timedelta


def collect_live_data(interval, duration, directory, *isin_list):

    start_time = datetime.now()
    client = ASAClient(config.ASA_COOKIE)

    while datetime.now() <= start_time + eval(duration):
        for isin in isin_list:
            opened_file = open(os.path.join(directory, isin), mode='a+', encoding='utf8')
            print(client.get_data_from_isin(isin), file=opened_file)
            opened_file.close()
        sleep(eval(interval))
