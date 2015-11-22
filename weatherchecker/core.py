#!/usr/bin/python3
import collections
import json
import os
import time
from typing import List, Dict, Union

import requests

from weatherchecker import helpers


class Core:
    def __init__(self) -> None:
        self.settings = Settings()
        self.params = {}
        wtypes = ('current', 'forecast')
        self.create_proxies(wtypes, self.params)
        self.histories = WeatherHistories(wtypes)

    def create_proxies(self, wtypes: tuple, params: Dict[str, str] = {}):
        self.proxies = {category: {} for category in wtypes}
        for category in self.proxies.keys():
            for source in self.settings.sources_info:
                self.proxies[category][source['name']] = WeatherProxy(url=source['urls'][category])

    def refresh(self, wtype):
        rtime = time.time()
        [proxy.refresh_data() for proxy in self.proxies[wtype].values()]

        source_data_map = {}
        for source in self.proxies[wtype].keys():
            source_data_map[source] = {}
            source_data_map[source]['raw'] = self.proxies[wtype][source].data
        self.histories.add_history_entry(time=str(rtime), wtype=wtype, source_data_map=source_data_map)


class WeatherHistories:
    def __init__(self, wtypes: tuple) -> None:
        self.__table = {wtype: [] for wtype in wtypes}
        self.entry_frame = {'time': '', 'wtype': '', 'data': {}}
        self.data_entry_frame = {'raw': '', 'measurements': {'temp': '', 'humidity': '', 'pressure': ''}}

    @property
    def dates(self) -> List[str]:
        try:
            output = [entry['time'] for entry in self.__table]
        except TypeError:
            output = []

        return output

    @property
    def entries(self) -> List[dict]:
        return json.loads(json.dumps(self.__table))

    def add_history_entry(self, time: str, wtype: str, source_data_map: Dict[str, Union[str, Dict[str, str]]]) -> None:
        entry = helpers.merge_dicts(self.entry_frame, {'time': time, 'wtype': wtype})
        for source in source_data_map.keys():
            entry['data'][source] = helpers.merge_dicts(self.data_entry_frame, source_data_map[source])
        self.__table[wtype].append(entry)


class WeatherProxy:
    def __init__(self, url: str, params: Dict[str, str] = {}) -> None:
        self.url = url
        self.params = collections.defaultdict(lambda: '')  # type: Dict[str, str]
        self.params.update(params)

    def refresh_data(self) -> None:
        response = requests.get(self.url % self.params)
        self.data = response.text
        self.status_code = response.status_code


class WeatherAdapter:
    def __init__(self) -> None:
        pass

    


class Settings:
    def __init__(self) -> None:
        module_path = os.path.dirname(__spec__.origin)
        defaults_path = os.path.join(module_path, 'default')

        settings_path = os.path.join(module_path, 'settings.toml')
        sources_frame_path = os.path.join(defaults_path, 'source_entry.toml')
        locations_frame_path = os.path.join(defaults_path, 'location_entry.toml')
        frame_paths = {'sources': sources_frame_path, 'locations': locations_frame_path}

        self.__table = {}

        raw_table = helpers.load_table(settings_path)

        # Process the data sources
        for category in ('sources', 'locations'):
            self.__table[category] = []
            frame = helpers.load_table(frame_paths[category])
            if category in raw_table.keys():
                for entry in raw_table[category]:
                    final_entry = helpers.merge_dicts(frame, entry)
                    self.__table[category].append(final_entry)


    @property
    def sources_list(self):
        s_list = set()
        for entry in self.__table['sources']:
            s_list.add(entry['name'])
        return json.loads(json.dumps(tuple(s_list)))

    @property
    def sources_info(self):
        return json.loads(json.dumps(self.__table['sources']))

    @property
    def locations(self):
        return json.loads(json.dumps(self.__table['locations']))
