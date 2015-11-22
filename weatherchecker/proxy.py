#!/usr/bin/python3
import collections
import requests
from typing import Dict

class WeatherProxy:
    def __init__(self, url: str, params: Dict[str, str] = {}) -> None:
        self.url = url
        self.params = collections.defaultdict(lambda: '')  # type: Dict[str, str]
        self.params.update(params)

    def refresh_data(self) -> None:
        response = requests.get(self.url % self.params)
        self.data = response.text
        self.status_code = response.status_code
