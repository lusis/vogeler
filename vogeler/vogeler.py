import json
import os, os.path
import shutil
import ConfigParser
import subprocess, shlex

from amqplib import client_0_8 as amqp
from platform import node
from glob import iglob

vhost = "/vogeler"
master_exchange = "vogeler.master.in"
broadcast_exchange = "vogeler.broadcast.out"
client_id = node()

def setup_client(host='', username='', password=''):
    node_name = client_id
    client_queue = node_name
    try:
        # Get a channel
        ch = setup_amqp(host, username, password)
        # define our incoming and outgoing queues
        ch.queue_declare(node_name, durable=True, auto_delete=False)
        # bind our queues to the channel
        ## this is for broadcast messages from the Vogeler server
        ch.queue_bind(client_queue, broadcast_exchange, routing_key='broadcasts.*')
        ## this is for messages intended for us over the same topic exchange
        ch.queue_bind(client_queue, broadcast_exchange, routing_key=node_name)
    except:
        raise
    return ch, client_queue

def setup_server(host='', username='', password=''):
    server_queue = 'master.in'
    try:
        # Get a channel
        ch = setup_amqp(host, username, password)
        # Setup our exchanges
        ## broadcast exchange for clients to recieve messages
        ch.exchange_declare(broadcast_exchange, 'topic', durable=True, auto_delete=False)
        ## direct exchange for server to get messages from clients
        ch.exchange_declare(master_exchange, 'direct', durable=True, auto_delete=False)
        # Now our own queues
        ch.queue_declare(server_queue, durable=True, auto_delete=False)
        # And then we bind to our channel
        ch.queue_bind(server_queue, master_exchange)
    except:
        raise
    return ch, server_queue

def setup_amqp(phost, puserid, ppassword):
    try:
        conn = amqp.Connection(host=phost,
            userid=puserid,
            password=ppassword,
            virtual_host=vhost,
            insist=False)
        ch = conn.channel()
        ch.access_request(vhost, active=True, read=True, write=True)
    except:
        raise
    return ch

class VogelerClient(object):
    def __init__(self, callback_function=None, **kwargs):
        try:
            self.ch, self.queue = setup_client(kwargs['host'], kwargs['username'], kwargs['password'])
            self.callback_function = callback_function
        except:
            raise VogelerException()

    def callback(self, msg):
        message = json.loads(msg.body)
        if(self.callback_function):
            self.callback_function(message)

    def monitor(self):
        try:
            print "Vogeler(Client) is starting up"
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
        except:
            raise VogelerException()

        while self.ch.callbacks:
            self.ch.wait()

    def message(self, message, durable=True):
        print "Vogeler(Client) is sending a message"
        msg = amqp.Message(json.dumps(message))
        if durable == True:
            msg.properties['delivery_mode'] = 2
        self.ch.basic_publish(msg, exchange=master_exchange)

    def close(self):
        self.ch.close()

class VogelerServer(object):
    def __init__(self, callback_function=None, **kwargs):
        try:
            self.ch, self.queue = setup_server(kwargs['host'], kwargs['username'], kwargs['password'])
            self.callback_function = callback_function
        except:
            raise VogelerException()

    def callback(self, msg):
        message = json.loads(msg.body)
        if(self.callback_function):
            self.callback_function(message)

    def monitor(self):
        try:
            print "Vogeler(Server) is starting up"
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
        except:
            raise VogelerException()

        while self.ch.callbacks:
            self.ch.wait()

    def message(self, message, durable=True):
        print "Vogeler(Server) is sending a message"
        msg = amqp.Message(json.dumps(message))
        if durable == True:
            msg.properties['delivery_mode'] = 2
        self.ch.basic_publish(msg, exchange=broadcast_exchange)

    def close(self):
        self.ch.close()

class VogelerRunner(object):
    def __init__(self, destination, **kwargs):
        self.routing_key = destination
        self.ch = setup_amqp(kwargs['host'], kwargs['username'], kwargs['password'])

    def message(self, message, durable=True):
        print "Vogeler(Runner) is sending a message"
        msg = amqp.Message(json.dumps(message))
        if durable == True:
            msg.properties['deliver_mode'] = 2
        self.ch.basic_publish(msg, exchange=broadcast_exchange, routing_key=self.routing_key)

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
            except subprocess.CalledProcessError:
                raise VogelerException(), "Failed to run command: "+self.plugin_registry[plugin]['command']
        else:
            raise VogelerException(), 'Command not authorized'

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
            raise VogelerException(), "Unable to compile plugin file"

    def _read_plugin_file(self):
        configobj = ConfigParser.SafeConfigParser()
        try:
            configobj.read(self.compiled_plugin_file)
            self._parse_plugin_file(config=configobj)
        except:
            raise VogelerException(), "Unable to read plugin file"

    def _parse_plugin_file(self, config):
        plugins = config.sections()
        print "Found plugins: %s" % plugins
        for plugin in plugins:
            plugin_details = dict(config.items(plugin))
            try:
                self._register_plugin(plugin_details)
                print "Registering plugin: %s" % plugin_details
            except:
                raise VogelerException(), "Registration failed for plugin "+plugin

        self._authorize_plugins()

    def _authorize_plugins(self):
        print "Authorizing registered plugins"
        try:
            self.authorized_plugins = tuple(self.plugin_registry.keys())
        except:
            raise

    def _register_plugin(self, plugin_details):
        plugin = plugin_details.pop("name")
        try:
            self.plugin_registry[plugin] = plugin_details
        except:
            raise
class VogelerEncryption(object):
    keyfile = '/etc/vogeler/encryption.key'
    pass

class VogelerException(Exception):
    pass

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
