"""
Routines to parse configuration file options.

"""

import ConfigParser


def get_namelist(args):
    """
    Return configuration options as <ConfigParser> object.
    
    """
    config = ConfigParser.ConfigParser()
    config.read(args.namelist)
    
    return config

