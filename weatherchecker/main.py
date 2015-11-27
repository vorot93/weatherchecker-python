#!/usr/bin/python3
from bottle import Bottle, request, template

from weatherchecker import core, helpers
from weatherchecker.global_settings import *

app = Bottle()
api = core.Api()

def index(name: str):
    return template('<b>Hello {{name}}</b>!', name=name)

def history_router(wtype: str):
    api.history_entries_all(wtype=str(wtype), source=request.query.source, location=request.query.location)

def add_location_router():
    args = {'accuweather_city_name': request.query.accuweather_city_name, 'gismeteo_city_name': request.query.gismeteo_city_name, 'country_name': request.query.country_name, 'longitude': request.query.longitude, 'gismeteo_id': request.query.gismeteo_id, 'iso_country': request.query.iso_country, 'city_name': request.query.city_name, 'latitude': request.query.latitude, 'accuweather_id': request.query.accuweather_id}

    output = api.add_location(**args)

    return output

def setup_routing(app):
    app.route('/hello/<name>', 'GET', index)
    app.route(ACTION_ENTRYPOINT + '/refresh', 'GET', api.refresh)
    app.route(ACTION_ENTRYPOINT + '/refresh/<wtype>', 'GET', api.refresh)
    app.route(ACTION_ENTRYPOINT + '/add_location', 'GET', add_location_router)
    app.route(DATA_ENTRYPOINT + '/environment', 'GET', api.environment)
    app.route(DATA_ENTRYPOINT + '/sources', 'GET', api.sources)
    app.route(DATA_ENTRYPOINT + '/locations', 'GET', api.locations)
    app.route(DATA_ENTRYPOINT + '/proxies', 'GET', api.proxies)
    app.route(DATA_ENTRYPOINT + '/history', 'GET', api.history_entries_all)
    app.route(DATA_ENTRYPOINT + '/history/<wtype>', 'GET', api.history_entries_all)

setup_routing(app)
app.run(server='cherrypy', host='0.0.0.0', port=8080)
