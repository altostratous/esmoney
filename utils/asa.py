import requests
import json
from datetime import datetime


class ASAClient:
    def __init__(self, cookies):
        super().__init__()

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': cookies,
            'DNT': '1',
            'Host': 'online.agah.com',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
        }

        self.session = requests.Session()
        self.session.headers = headers

    def _get_json_from_url(self, url):
        response = self.session.get(url)
        data = json.loads(response.text)
        data['Time'] = datetime.now()
        return data

    def get_data_from_isin(self, isin):
        return self._get_json_from_url('https://online.agah.com/Watch/GetInstrumentInfo?isin={}'.format(isin))
