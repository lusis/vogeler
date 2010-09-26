import ConfigParser
import os, shutil, subprocess, shlex

from platform import node
from glob import iglob

import vogeler.exceptions as exceptions
import vogeler.logger as logger
import vogeler.conf as conf

class VogelerPlugin(object):
    compiled_plugin_file = '/tmp/vogeler-plugins.cfg'
    authorized_plugins = ()
    plugin_registry = {}
    def __init__(self, plugin_dir='/etc/vogeler/plugins', **kwargs):
        self._configured = False

        if kwargs.has_key("config"):
            self._configure(kwargs["config"])
            self._configured = True

        if kwargs.has_key("loglevel"):
            log_level = kwargs["loglevel"]
        elif self._configured is True and self._config.has_option('global', 'log_level'):
            log_level = self._config.get('global', 'log_level')
        else:
            log_level = 'WARN'

        self.log = logger.LogWrapper(name='vogeler-plugins', level=log_level).logger()

        self.log.info("Vogeler is parsing plugins")
        self.registered_plugins = {}
        self.plugin_dir = plugin_dir
        self._compile_plugins()

    def _configure(self, config_file=None):
        if config_file is not None:
            self._config = conf.configure(cfg=config_file)

    def execute_plugin(self, plugin):
        if plugin in self.authorized_plugins:
            try:
                command = self.plugin_registry[plugin]['command']
                plugin_format = self.plugin_registry[plugin]['result_format']
                result = subprocess.Popen(shlex.split(command), stdout = subprocess.PIPE).communicate()
                return self.format_response(plugin, result, plugin_format)
            except Exception, e:
                self.log.warn("Unable to execute plugin: %s" % command)
                self.log.debug("Plugin execution log: %s" % e)
                raise
        else:
            self.log.warn("Plugin %s not authorized for this host. Ignoring" % plugin)
            raise exceptions.VogelerPluginAuthorizationException()

    def format_response(self, plugin, output, plugin_format):
        message = { 'syskey' : node(), plugin : output[0], 'format' : plugin_format }
        self.log.debug("Message: %s" % message)
        return message

    def _compile_plugins(self):
        try:
            cpf = open(self.compiled_plugin_file, 'w')
            header = "#This is a compiled vogeler plugin file. Please do not edit!!!\n"
            cpf.write(header)
            for filename in iglob(os.path.join(self.plugin_dir, '*.cfg')):
                shutil.copyfileobj(open(filename, 'r'), cpf)
            cpf.close()
            self._read_plugin_file()
        except Exception, e:
            self.log.fatal("Unable to compile plugin file: %s" % e)
            raise exceptions.VogelerPluginCompilationException()

    def _read_plugin_file(self):
        configobj = ConfigParser.SafeConfigParser()
        try:
            configobj.read(self.compiled_plugin_file)
            self._parse_plugin_file(config=configobj)
        except Exception, e:
            self.log.fatal("Unable to parse compiled plugin file: %s" % e)
            raise exceptions.VogelerPluginCompiledParsingException()

    def _parse_plugin_file(self, config):
        plugins = config.sections()
        self.log.info("Found plugins: %s" % plugins)
        for plugin in plugins:
            plugin_details = dict(config.items(plugin))
            try:
                self._register_plugin(plugin_details)
                self.log.info("Registering plugin: %s" % plugin_details)
            except Exception, e:
                self.log.warn("Unable to parse plugin file: %s. Ignoring. %s" % (plugin, e))
                raise exceptions.VogelerPluginParsingException()

        self._authorize_plugins()

    def _authorize_plugins(self):
        self.log.info("Authorizing registered plugins")
        try:
            self.authorized_plugins = tuple(self.plugin_registry.keys())
        except Exception, e:
            self.log.warn("Unable to authorize plugins: %s" % self.plugin_registry.keys())
            self.log.debug("Exception: %s" % e)
            raise exceptions.VogelerPluginAuthorizationException()

    def _register_plugin(self, plugin_details):
        plugin = plugin_details.pop("name")
        try:
            self.plugin_registry[plugin] = plugin_details
        except Exception, e:
            self.log.warn("Unable to register plugin: %s" % plugin)
            self.log.debug("Exception: %s" % e)
            raise exceptions.VogelerPluginRegistrationException()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
