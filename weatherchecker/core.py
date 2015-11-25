#!/usr/bin/python3
import collections
import itertools
import json
import os
import threading
import time
from typing import List, Dict, Sequence, Union

import requests

from weatherchecker import helpers


class Core:
    def __init__(self) -> None:
        self.settings = Settings()
        wtypes = ('current', 'forecast')
        sources = self.settings.sources_info
        locations = self.settings.locations
        params = self.settings.general
        self.proxies = WeatherProxyTable(wtypes, sources, locations, params)
        self.histories = WeatherHistories(wtypes)

    def refresh(self, wtype):
        rtime = time.time()
        self.proxies.refresh(wtype)

        source_data_map = collections.defaultdict(lambda: {})
        for entry in helpers.db_find(self.proxies.proxy_info, {'wtype': wtype}):
            source = entry['source']
            source_data_map[source]['raw'] = entry['data']
        self.histories.add_history_entry(time=str(rtime), wtype=wtype, source_data_map=source_data_map)


class WeatherHistories:
    def __init__(self, wtypes: Sequence[str]) -> None:
        self.__table = {wtype: [] for wtype in wtypes}
        self.entry_schema = {'time': '', 'wtype': '', 'data': {}}
        self.data_entry_schema = {'raw': '', 'measurements': {'temp': '', 'humidity': '', 'pressure': ''}}

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
        entry = helpers.merge_dicts(self.entry_schema, {'time': time, 'wtype': wtype})
        for source in source_data_map.keys():
            entry['data'][source] = helpers.merge_dicts(self.data_entry_schema, source_data_map[source])
        self.__table[wtype].append(entry)


class LocationTable:
    pass


class WeatherProxyTable:
    def __init__(self, wtypes: tuple, sources_info: Dict[str, str], locations: Sequence[Dict[str, str]], params: Dict[str, str] = []):
        self.__table = []
        self.wtypes = wtypes
        self.sources_info = sources_info
        self.proxy_entry_schema = {'proxy': None, 'wtype': '', 'source': '', 'location': None}
        for location in locations:
             self.add_location(location, params)

    def add_location(self, location: Dict[str, str], params: Dict[str, str]):
        for category, source in itertools.product(self.wtypes, self.sources_info):
            url_params = {}
            url_params.update(location)
            url_params.update(params)
            entry = helpers.merge_dicts(self.proxy_entry_schema, {'proxy': WeatherProxy(url=source['urls'][category], url_params=url_params), 'wtype': category, 'source': source['name'], 'location': location})
            helpers.db_add(self.__table, entry)

    def remove_location(self, location: Dict[str, str]):
        helpers.db_remove(self.__table, {'location': location})

    def refresh(self, wtype: str):
        threads = []
        for entry in helpers.db_find(self.__table, {'wtype': wtype}):
            t = threading.Thread(target=(self.__refresh_thread), kwargs={'proxy': entry['proxy']})
            t.daemon = True
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def __refresh_thread(self, proxy):
        proxy.refresh_data()

    @property
    def proxy_info(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        info = []
        for entry in self.__table:
            wtype = entry['wtype']
            source = entry['source']
            location = entry['location']
            proxy = entry['proxy']
            info_entry = {'wtype': wtype, 'source': source, 'data': proxy.data, 'url': proxy.url, 'location': location}
            info.append(info_entry)
        return info


class WeatherProxy:
    def __init__(self, url: str, url_params: str) -> None:
        self.url_params = collections.defaultdict(lambda: '')  # type: Dict[str, str]
        self.url_params.update(url_params)
        self.url = url % self.url_params
        self.data = None
        self.status_code = None

    def refresh_data(self) -> None:
        response = requests.get(self.url)
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
        schema_paths = {'sources': os.path.join(defaults_path, 'source_entry_schema.toml'), 'locations': os.path.join(defaults_path, 'location_entry_schema.toml'), 'general': os.path.join(defaults_path, 'general_schema.toml')}

        schemas = {category: helpers.load_table(schema_paths[category]) for category in schema_paths.keys()}

        self.__table = {}

        raw_table = helpers.load_table(settings_path)

        # Process the categories in settings in a safe manner
        for category in schemas.keys():
            self.__table[category] = []
            schema = schemas[category]
            if category in raw_table.keys():
                if isinstance(raw_table[category], list):
                    for entry in raw_table[category]:
                        final_entry = helpers.merge_dicts(schema, entry)
                        self.__table[category].append(final_entry)
                else:
                    self.__table[category].append(helpers.merge_dicts(schema, raw_table[category]))


    @property
    def sources_list(self):
        output = set()
        for entry in self.__table['sources']:
            output.add(entry['name'])
        return json.loads(json.dumps(tuple(output)))

    @property
    def sources_info(self):
        return json.loads(json.dumps(self.__table['sources']))

    @property
    def locations(self):
        return json.loads(json.dumps(self.__table['locations']))

    @property
    def general(self):
        return json.loads(json.dumps(self.__table['general'][0]))
