"""
    Author: John E. Vincent
	Email:	jvincent@tsys.com
	Date:	08/19/2010
"""
import json

from amqplib import client_0_8 as amqp
from platform import node

ruser = "guest"
rpass = "guest"
default_host = "localhost"
vhost = "/vogeler"
master_exchange = "vogeler.master.in"
broadcast_exchange = "vogeler.broadcast.out"
default_role = 'client'
client_id = node()

def setup_client(host=''):
    if host == '':
        host = default_host
    node_name = client_id
    client_queue = node_name
    try:
        # Get a channel
        ch = setup_amqp(host)
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
        
def setup_server(host=''):
    if host == '':
        host = default_host
    server_queue = 'master.in'
    try:
        # Get a channel
        ch = setup_amqp(host)
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

def setup_amqp(queue_host):
    try:
        conn = amqp.Connection(host=queue_host, userid=ruser, password=rpass, virtual_host=vhost, insist=False)
        ch = conn.channel()
        ch.access_request(vhost, active=True, read=True, write=True)
    except:
        raise
    return ch

class VogelerClient(object):
    def __init__(self, callback_function=None):
        self.ch, self.queue = setup_client()
        self.callback_function = callback_function

    def callback(self, msg):
        message = json.loads(msg.body)
        if(self.callback_function):
            self.callback_function(message)

    def monitor(self):
        try:
            print "Vogeler(Client) is starting up"
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
        except:
            raise
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
    def __init__(self, callback_function=None):
        self.ch, self.queue = setup_server()
        self.callback_function = callback_function

    def callback(self, msg):
        message = json.loads(msg.body)
        if(self.callback_function):
            self.callback_function(message)

    def monitor(self):
        try:
            print "Vogeler(Server) is starting up"
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
        except:
            raise
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
    def __init__(self, destination, host=''):
        if host == '':
            host = default_host
        self.routing_key = destination
        self.ch = setup_amqp(host)

    def message(self, message, durable=True):
        print "Vogeler(Runner) is sending a message"
        msg = amqp.Message(json.dumps(message))
        if durable == True:
            msg.properties['deliver_mode'] = 2
        self.ch.basic_publish(msg, exchange=broadcast_exchange, routing_key=self.routing_key)

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
