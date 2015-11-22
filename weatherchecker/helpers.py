#!/usr/bin/python3
import pytoml
import types
from typing import Any, Dict

def load_table(path: str) -> dict:
        """Loads settings table into dict"""
        try:
            table_open_object = open(path, 'r')
        except FileNotFoundError:
            return {}
        table = pytoml.load(table_open_object)
        return table


def merge_dicts(x: Dict[Any, Any], y: Dict[Any, Any]) -> Dict[Any, Any]:
    # store a copy of x, but overwrite with y's values where applicable
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
