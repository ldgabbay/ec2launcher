# -*- coding: utf-8 -*-

from ec2launcher import Configuration, launch

import cjson
import os


def load_configurations(*args):
    filenames = ['./.footstrap', '~/.footstrap', '/etc/footstrap']
    if args:
        filenames = list(args) + filenames
    for filename in filenames:
        try:
            with open(os.path.expanduser(filename), 'r') as in_file:
                return cjson.decode(in_file.read())
        except:
            pass
    return {}
