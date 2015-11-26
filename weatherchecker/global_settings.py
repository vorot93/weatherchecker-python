GENERAL_SETTINGS_SCHEMA = {'owm_key': '', 'forecastio_key': '', 'myweather2_key': '', 'myweather2_uref': '', 'worldweatheronline_key': '', 'wunderground_key': ''}
LOCATION_ENTRY_SCHEMA = {'accuweather_city_name': '', 'gismeteo_city_name': '', 'country_name': '', 'longitude': '', 'gismeteo_id': '', 'iso_country': '', 'city_name': '', 'latitude': '', 'accuweather_id': ''}
SOURCE_ENTRY_SCHEMA = {'name': '', 'stype': '', 'urls': {'current', 'forecast'}}
HISTORY_ENTRY_SCHEMA = {'time': '', 'wtype': '', 'data': []}
HISTORY_DATA_ENTRY_SCHEMA = {'location': LOCATION_ENTRY_SCHEMA, 'source': SOURCE_ENTRY_SCHEMA, 'measurements': {'temp': '', 'humidity': '', 'pressure': ''}}

API_ENTRYPOINT = "/api"
ACTION_ENTRYPOINT = API_ENTRYPOINT + "/actions"
DATA_ENTRYPOINT = API_ENTRYPOINT + "/data"
