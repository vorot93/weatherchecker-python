import json

def adapt_weather(wtype, source, data):
    weather = globals()[source + "_" + wtype + "_weather"](data)
    return weather


def openweathermap_current_weather(data):
    weather_hash = json.loads(data)
    weather = {}
    try:
        weather['temp'] = float(weather_hash['main']['temp'])
    except (KeyError, ValueError):
        pass

    try:
        weather['precipitation'] = float(weather_hash['rain']['3h'])
    except (KeyError, ValueError):
        try:
            weather['precipitation'] = float(weather_hash['snow']['3h'])
        except (KeyError, ValueError):
            pass

    try:
        weather['pressure'] = float(weather_hash['main']['pressure'])
    except (KeyError, ValueError):
        pass

    try:
        weather['wind'] = float(weather_hash['wind']['speed'])
    except (KeyError, ValueError):
        pass

    return weather


def wunderground_current_weather(data):
    weather_hash = json.loads(data)
    weather = {}

    try:
        weather['temp'] = float(weather_hash['current_observation']['temp_c'])
    except (KeyError, ValueError):
        pass

    try:
        weather['precipitation'] = float(weather_hash['current_observation']['precip_today_metric'])
    except (KeyError, ValueError):
        pass

    try:
        weather['pressure'] = float(weather_hash['current_observation']['pressure_mb'])
    except (KeyError, ValueError):
        pass

    try:
        weather['wind'] = float(weather_hash['current_observation']['wind_kph']) / 3.6
    except (KeyError, ValueError):
        pass

    return weather


def myweather2_current_weather(data):
    weather_hash = json.loads(data)
    weather = {}

    try:
        weather['temp'] = float(weather_hash['weather']['curren_weather'][0]['temp'])
    except (KeyError, ValueError):
        pass

    try:
        weather['precipitation'] = ''
    except (KeyError, ValueError):
        pass

    try:
        weather['pressure'] = float(weather_hash['weather']['curren_weather'][0]['pressure'])
    except (KeyError, ValueError):
        pass

    try:
        weather['wind'] = float(weather_hash['weather']['curren_weather'][0]['wind'][0]['speed']) / 2.23
    except (KeyError, ValueError):
        pass

    return weather
