from amqplib import client_0_8 as amqp
from platform import node

from vogeler.exceptions import VogelerException

#.. attribute::`vogeler.queue.amqp.vhost`
vhost = "/vogeler"
master_exchange = "vogeler.master.in"
broadcast_exchange = "vogeler.broadcast.in"
client_id = node()

def setup_client(host='', username='', password=''):
    """Setup a client AMQP binding"""
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
    """Setup a server AMQP binding"""
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
    """Generic AMQP channel creation"""
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

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
