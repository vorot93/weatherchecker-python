#!/usr/bin/python3
from bottle import Bottle

from weatherchecker import core, proxy

app = Bottle()

@app.route('/hello/<name>')
def index(name: str) -> Bottle.template:
    return app.template('<b>Hello {{name}}</b>!', name=name)

app.run(host='localhost', port=8080)
