import ConfigParser

import vogeler.exceptions as exceptions
import vogeler.logger as logger

DEFAULT_CONFIG_FILE = '/etc/vogeler/vogeler.conf'
log = logger.LogWrapper(name='vogeler').logger()

def _read_global_config(cfg):
    configparser = ConfigParser.RawConfigParser()

    try:
        configparser.readfp(open(cfg))
    except IOError, e:
        log.fatal("Unable to read global config")
        raise VogelerConfigurationException(e)
    return configparser

def configure(cfg=None):
    if cfg is not None:
        config_file = cfg
    else:
        config_file = DEFAULT_CONFIG_FILE
    config = _read_global_config(config_file)
    return config

class VogelerConfigurationException(exceptions.VogelerException): pass
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
