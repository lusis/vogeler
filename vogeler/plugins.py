import ConfigParser
import os, shutil, subprocess, shlex

from platform import node
from glob import iglob

from vogeler.exceptions import VogelerException

class VogelerPlugin(object):
    compiled_plugin_file = '/tmp/vogeler-plugins.cfg'
    authorized_plugins = ()
    plugin_registry = {}
    def __init__(self, plugin_dir='/etc/vogeler/plugins'):
        print "Vogeler is parsing plugins"
        self.registered_plugins = {}
        self.plugin_dir = plugin_dir
        self._compile_plugins()

    def execute_plugin(self, plugin):
        if plugin in self.authorized_plugins:
            try:
                command = self.plugin_registry[plugin]['command']
                plugin_format = self.plugin_registry[plugin]['result_format']
                result = subprocess.Popen(shlex.split(command), stdout = subprocess.PIPE).communicate()
                return self.format_response(plugin, result, plugin_format)
            except:
                raise VogelerException()
        else:
            raise VogelerException()

    def format_response(self, plugin, output, plugin_format):
        message = { 'syskey' : node(), plugin : output[0], 'format' : plugin_format }
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
        except:
            raise VogelerException()

    def _read_plugin_file(self):
        configobj = ConfigParser.SafeConfigParser()
        try:
            configobj.read(self.compiled_plugin_file)
            self._parse_plugin_file(config=configobj)
        except:
            raise VogelerException()

    def _parse_plugin_file(self, config):
        plugins = config.sections()
        print "Found plugins: %s" % plugins
        for plugin in plugins:
            plugin_details = dict(config.items(plugin))
            try:
                self._register_plugin(plugin_details)
                print "Registering plugin: %s" % plugin_details
            except:
                raise VogelerException()

        self._authorize_plugins()

    def _authorize_plugins(self):
        print "Authorizing registered plugins"
        try:
            self.authorized_plugins = tuple(self.plugin_registry.keys())
        except:
            raise VogelerException()

    def _register_plugin(self, plugin_details):
        plugin = plugin_details.pop("name")
        try:
            self.plugin_registry[plugin] = plugin_details
        except:
            raise VogelerException()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
