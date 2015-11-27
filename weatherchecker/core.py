#!/usr/bin/python3
import collections
import itertools
import json
import os
import threading
import time
from typing import Callable, Dict, List, Sequence, Union

import requests

from weatherchecker import adapters, helpers
from weatherchecker.global_settings import *


class Api:
    def __init__(self) -> None:
        self.core = Core()

    def refresh(self, wtype: str = ""):
        if wtype in self.core.wtypes:
            data = self.core.refresh(wtype)['history_entry']
            output = {'status': 200, 'entry': data}
        else:
            output = 'Please specify a correct wtype'

        return output

    def add_location(self, accuweather_city_name: str = '', gismeteo_city_name: str = '', country_name: str = '', longitude: str = '', gismeteo_id: str = '', iso_country: str = '', city_name: str = '', latitude: str = '', accuweather_id: str = ''):

        location = helpers.merge_dicts(LOCATION_ENTRY_SCHEMA, {'accuweather_city_name': accuweather_city_name, 'gismeteo_city_name': gismeteo_city_name, 'country_name': country_name, 'longitude': longitude, 'gismeteo_id': gismeteo_id, 'iso_country': iso_country, 'city_name': city_name, 'latitude': latitude, 'accuweather_id': accuweather_id})

        output = self.core.proxies.add_location(location, self.environment()['environment'])

        return {'status': 200, 'data': output}

    def remove_location(self, location_id):
        pass

    def environment(self):
        data = {'environment': self.core.settings.environment}
        return data

    def sources(self):
        data = {'sources': self.core.settings.sources_info}
        return data

    def locations(self):
        data = {'locations': self.core.settings.locations}
        return data

    def proxies(self):
        data = {'proxy_info': self.core.proxies.proxy_info}
        return data

    def history_entries_all(self, wtype: str = "", source = {}, location = {}):
        if wtype not in WTYPES:
            return 'Please specify correct forecast type'

        search_string = {}

        if source:
            source = helpers.db_find(self.sources()['source'], {'name': request.query.source})[0]
            search_string['source'] = source

        if location:
            location = helpers.db_find(self.locations()['location'], {'name': request.query.location})[0]
            search_string['location'] = location

        history = self.core.history.entries
        try:
            data = {'history': helpers.db_find(history, {'wtype': wtype})}
        except (IndexError, KeyError):
            print(history)
            data = {'history': []}
        return data


class Core:
    def __init__(self) -> None:
        self.settings = Settings()
        self.wtypes = WTYPES
        sources = self.settings.sources_info
        locations = self.settings.locations
        params = self.settings.environment
        self.proxies = WeatherProxyTable(self.wtypes, sources, locations, params)
        self.history = WeatherHistory(self.wtypes)

    def refresh(self, wtype):
        rtime = time.time()
        self.proxies.refresh(wtype)
        history_entry = self.history.add_history_entry(time=str(rtime), wtype=wtype, raw_data_map=self.proxies.proxy_info)

        return {'history_entry': history_entry}


class WeatherHistory:
    def __init__(self, wtypes: Sequence[str]) -> None:
        self.__table = []
        self.entry_schema = HISTORY_ENTRY_SCHEMA
        self.data_entry_schema = HISTORY_DATA_ENTRY_SCHEMA

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

    def add_history_entry(self, time: str, wtype: str, raw_data_map: Sequence[Dict[str, Union[str, dict]]]) -> None:
        entry = helpers.merge_dicts(self.entry_schema, {'time': time, 'wtype': wtype})
        for raw_entry in raw_data_map:
            data = raw_entry['data']
            location = raw_entry['location']
            source = raw_entry['source']
            try:
                measurements = adapters.adapt_weather(wtype, source['name'].lower(), data)
            except:
                measurements = {}
            history_entry = {'location': location, 'source': source, 'measurements': measurements}
            helpers.db_add(entry['data'], helpers.merge_dicts(self.data_entry_schema, history_entry))
        helpers.db_add(self.__table, entry)

        return json.loads(json.dumps(entry))


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
        output = []
        for category, source in itertools.product(self.wtypes, self.sources_info):
            url_params = {}
            url_params.update(location)
            url_params.update(params)
            entry = helpers.merge_dicts(self.proxy_entry_schema, {'proxy': WeatherProxy(url=source['urls'][category], url_params=url_params), 'wtype': category, 'source': source, 'location': location})
            helpers.db_add(self.__table, entry)
            output.append(self.single_proxy_info(entry))

        return output

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
            info_entry = single_proxy_info(entry)
            info.append(info_entry)
        return info

    @staticmethod
    def single_proxy_info(entry) -> Dict[str, str]:
        wtype = entry['wtype']
        source = entry['source']
        location = entry['location']
        proxy = entry['proxy']
        info_entry = {'wtype': wtype, 'source': source, 'data': proxy.data, 'url': proxy.url, 'location': location}

        return json.loads(json.dumps(info_entry))


class WeatherProxy:
    def __init__(self, url: str, url_params: Dict[str, str]) -> None:
        self.url_params = collections.defaultdict(lambda: '')  # type: Dict[str, str]
        self.url_params.update(url_params)
        self.url = url % self.url_params
        self.data = None
        self.status_code = None

    def refresh_data(self) -> None:
        try:
            response = requests.get(self.url)
            self.data = response.text
            self.status_code = response.status_code
        except requests.exceptions.ConnectionError:
            self.data = ""
            self.status_code = 404


class Settings:
    def __init__(self) -> None:
        module_path = os.path.dirname(__spec__.origin)
        settings_path = os.path.join(module_path, 'settings.toml')
        schemas = {'sources': SOURCE_ENTRY_SCHEMA, 'locations': LOCATION_ENTRY_SCHEMA}

        self.__table = {}

        raw_table = helpers.load_table(settings_path)

        self.load_settings(self.__table, raw_table, schemas)

        self.__table['env'] = helpers.merge_dicts(ENV_SETTINGS_SCHEMA, dict(os.environ))

    @staticmethod
    def load_settings(main_table, raw_table, schemas):
        '''Process the categories in settings in a safe manner'''
        for category in schemas.keys():
            main_table[category] = []
            schema = schemas[category]
            if category in raw_table.keys():
                if isinstance(raw_table[category], list):
                    for entry in raw_table[category]:
                        final_entry = helpers.merge_dicts(schema, entry)
                        main_table[category].append(final_entry)
                else:
                    main_table[category].append(helpers.merge_dicts(schema, raw_table[category]))


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
    def environment(self):
        return json.loads(json.dumps(self.__table['env']))
