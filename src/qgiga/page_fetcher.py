import random
import time

import requests


class PageFetcher:

    def __init__(self):
        pass

    @classmethod
    def fetch_html(cls, url: str):
        time.sleep(random.uniform(0.2, 1))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://vodcnd11.rsfcxq.com/",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "text/plain,*/*",
        }
        session = requests.Session()
        response = session.get("https://m.qgiga.com{}".format(url), headers=headers)
        if response.status_code != 200:
            raise ConnectionError("网站访问异常: {}".format(url))
        return response.text
