#!/usr/bin/python3
from bottle import Bottle, template

from weatherchecker import core
from weatherchecker.global_settings import *

app = Bottle()
core_instance = core.Core()

def index(name: str):
    return template('<b>Hello {{name}}</b>!', name=name)

def api_refresh(wtype: str = ""):
    wtype_str = str(wtype)
    if wtype_str in core_instance.wtypes:
        core_instance.refresh(wtype_str)
        output = 'Data refreshed successfully'
    else:
        output = 'Please specify a correct wtype'

    return output

def api_sources():
    data = {'sources': core_instance.settings.sources_info}
    return data

def api_locations():
    data = {'locations': core_instance.settings.locations}
    return data

def api_proxies():
    data = {'proxy_info': core_instance.proxies.proxy_info}
    return data

def setup_routing(app):
    app.route('/hello/<name>', 'GET', index)
    app.route(ACTION_ENTRYPOINT + '/refresh', 'GET', api_refresh)
    app.route(ACTION_ENTRYPOINT + '/refresh/<wtype>', 'GET', api_refresh)
    app.route(DATA_ENTRYPOINT + '/sources', 'GET', api_sources)
    app.route(DATA_ENTRYPOINT + '/locations', 'GET', api_locations)
    app.route(DATA_ENTRYPOINT + '/proxies', 'GET', api_proxies)

setup_routing(app)
app.run(host='localhost', port=8080)
