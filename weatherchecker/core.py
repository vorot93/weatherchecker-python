#!/usr/bin/python3
import json
import os

from weatherchecker import helpers, proxy


class Core:
    def __init__(self) -> None:
        self.settings = Settings()
        self.params = {}
        self.create_proxies(('current', 'forecast'), {})

    def create_proxies(self, categories, params={}):
        self.proxies = {category: {} for category in categories}
        for category in self.proxies.keys():
            for source in self.settings.sources_info:
                self.proxies[category][source['name']] = proxy.WeatherProxy(url=source['urls'][category])


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
