import json

def adapt_weather(wtype, source, data):
        weather = globals()[source + "_" + wtype + "_weather"](data)
        return weather

def openweathermap_current_weather(data):
        weather_hash = json.loads(data)
        weather = {}
        try:
            weather['temp'] = float(weather_hash['main']['temp'])
        except KeyError:
            pass

        try:
            weather['precipitation'] = float(weather_hash['rain']['3h'])
        except KeyError:
            try:
                weather['precipitation'] = float(weather_hash['snow']['3h'])
            except KeyError:
                pass

        try:
            weather['pressure'] = float(weather_hash['main']['pressure'])
        except KeyError:
            pass

        try:
            weather['wind'] = float(weather_hash['wind']['speed'])
        except KeyError:
            pass

        return weather


