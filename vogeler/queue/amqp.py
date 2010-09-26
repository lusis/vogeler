import urlparse
from amqplib import client_0_8 as amqp
from platform import node

import vogeler.logger as logger
import vogeler.exceptions as exceptions

log = logger.LogWrapper(name='vogeler', level='WARN').logger()

#.. attribute::`vogeler.queue.amqp.vhost`
default_dsn = "amqp://guest:guest@127.0.0.1:5762/vogeler"
master_exchange = "vogeler.master.in"
broadcast_exchange = "vogeler.broadcast.in"
client_id = node()

def setup_client(dsn=None, **kwargs):
    """Setup a client AMQP binding"""
    node_name = client_id
    client_queue = node_name
    if dsn is not None:
        _dsn = dsn
    else:
        _dsn = default_dsn

    try:
        # Get a channel
        ch = setup_amqp(_dsn, **kwargs)
        # define our incoming and outgoing queues
        ch.queue_declare(node_name, durable=True, auto_delete=False)
        # bind our queues to the channel
        ## this is for broadcast messages from the Vogeler server
        ch.queue_bind(client_queue, broadcast_exchange, routing_key='broadcasts.*')
        ## this is for messages intended for us over the same topic exchange
        ch.queue_bind(client_queue, broadcast_exchange, routing_key=node_name)
    except Exception, e:
        raise Exception(e)
    return ch, client_queue

def setup_server(dsn=None, **kwargs):
    """Setup a server AMQP binding"""
    server_queue = 'master.in'
    try:
        # Get a channel
        ch = setup_amqp(dsn, **kwargs)
        # Setup our exchanges
        ## broadcast exchange for clients to recieve messages
        ch.exchange_declare(broadcast_exchange, 'topic', durable=True, auto_delete=False)
        ## direct exchange for server to get messages from clients
        ch.exchange_declare(master_exchange, 'direct', durable=True, auto_delete=False)
        # Now our own queues
        ch.queue_declare(server_queue, durable=True, auto_delete=False)
        # And then we bind to our channel
        ch.queue_bind(server_queue, master_exchange)
    except Exception, e:
        raise Exception(e)
    return ch, server_queue

def setup_amqp(dsn=None, **kwargs):
    """Generic AMQP channel creation"""
    if dsn is not None:
        _dsn = dsn
    else:
        _dsn = default_dsn

    _parsed = urlparse.urlparse(_dsn)
    u, p, h, pt, vh = ( _parsed.username, _parsed.password, _parsed.hostname, _parsed.port, _parsed.path )

    try:
        conn = amqp.Connection(host=h,
            port=pt,
            userid=u,
            password=p,
            virtual_host=vh,
            insist=False)
        ch = conn.channel()
        ch.access_request(vh, active=True, read=True, write=True)
    except Exception, e:
        log.fatal("Unable to connect to setup amqp channels")
        raise Exception(e)
    return ch

class VogelerAMQPException(exceptions.VogelerMessagingException): pass
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
