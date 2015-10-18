# -*- coding: utf-8 -*-

from foolaunch import Configuration, launch

import cjson
import os


def load_configurations(*args):
    filenames = ['./.foolaunch', '~/.foolaunch', '/etc/foolaunch']
    if args:
        filenames = list(args) + filenames
    body = None
    for filename in filenames:
        try:
            with open(os.path.expanduser(filename), 'rb') as f:
                body = f.read()
        except:
            continue
    if body:
        return cjson.decode(body)
    else:
        return {}
