ENV_SETTINGS_SCHEMA = {'OWM_KEY': '', 'FORECASTIO_KEY': '', 'MYWEATHER2_KEY': '', 'MYWEATHER2_UREF': '', 'WORLDWEATHERONLINE_KEY': '', 'WUNDERGROUND_KEY': ''}
LOCATION_ENTRY_SCHEMA = {'accuweather_city_name': '', 'gismeteo_city_name': '', 'country_name': '', 'longitude': '', 'gismeteo_id': '', 'iso_country': '', 'city_name': '', 'latitude': '', 'accuweather_id': ''}
SOURCE_ENTRY_SCHEMA = {'name': '', 'urls': {'current', 'forecast'}}
HISTORY_ENTRY_SCHEMA = {'time': '', 'wtype': '', 'data': []}
MEASUREMENT_SCHEMA = {'temp': '', 'humidity': '', 'pressure': '', 'precipitation': '', 'wind': ''}
HISTORY_DATA_ENTRY_SCHEMA = {'location': LOCATION_ENTRY_SCHEMA, 'source': SOURCE_ENTRY_SCHEMA, 'measurements': MEASUREMENT_SCHEMA}

WTYPES = ('current', 'forecast')

API_ENTRYPOINT = "/api"
ACTION_ENTRYPOINT = API_ENTRYPOINT + "/actions"
DATA_ENTRYPOINT = API_ENTRYPOINT + "/data"
