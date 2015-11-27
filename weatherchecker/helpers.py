#!/usr/bin/python3
import pytoml
import types
from typing import Any, Dict, List

def load_table(path: str) -> dict:
        """Loads settings table into dict"""
        try:
            table_open_object = open(path, 'r')
        except FileNotFoundError:
            return {}
        table = pytoml.load(table_open_object)
        return table


def db_find(table: List[dict], query: Dict[Any, Any]):
    new_table = table
    for criterium in query.keys():
        key = criterium
        value = query[key]
        new_table = list(filter(lambda new_table: new_table[key] == value, new_table))
    return new_table


def db_remove(table: List[dict], query: Dict[Any, Any]):
    found_list = db_find(table, query)
    for entry in found_list:
        while True:
            try:
                table.remove(entry)
            except ValueError:
                break


def db_add(table: List[dict], entry: Dict[Any, Any]):
    table.append(entry)


def merge_dicts(x: Dict[Any, Any], y: Dict[Any, Any]) -> Dict[Any, Any]:
    # store a copy of x, but overwrite with y's values where applicable
    if not (isinstance(x, dict) and isinstance(y, dict)):
        raise TypeError('This function is only applicable to dictionaries. Attempted to merge %(x)s and %(y)s' % {'x': x, 'y': y})
    xkeys = x.keys()

    merged = {}

    # if the value of merged[key] was overwritten with y[key]'s value
    # then we need to put back any missing x[key] values
    for key in xkeys:
        # if this key is a dictionary, recurse
        if isinstance(x[key], dict) and key in y:
            merged[key] = merge_dicts(x[key],y[key])
        else:
            merged[key] = x[key]
            try:
                merged[key] = y[key]
            except KeyError:
                pass

    return merged


def output_data(data):
    return {'status': 200, 'message': '', 'data': data}


def output_error(msg):
    return {'status': 500, 'message': msg}
