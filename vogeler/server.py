import json

import vogeler.log as logger
from vogeler.exceptions import VogelerServerException
from vogeler.messaging import amqp

log = logger.setup_logger(logLevel='DEBUG', logFile=None, name='vogeler-server')
class VogelerServer(object):
    def __init__(self, callback_function=None, **kwargs):
        try:
            self.ch, self.queue = amqp.setup_server(kwargs['host'], kwargs['username'], kwargs['password'])
            self.callback_function = callback_function
        except:
            raise VogelerServerException("Unable to connect to messaging system on %s as %s" % (kwargs['host'], kwargs['username']))

    def callback(self, msg):
        message = json.loads(msg.body)
        if(self.callback_function):
            self.callback_function(message)

    def monitor(self):
        try:
            log.info("Vogeler(Server) is starting up")
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
        except:
            raise VogelerServerException("Unable to consume queue")

        while self.ch.callbacks:
            self.ch.wait()

    def message(self, message, durable=True):
        log.info("Vogeler(Server) is sending a message")
        try:
            msg = amqp.amqp.Message(json.dumps(message))
            if durable == True:
                msg.properties['delivery_mode'] = 2
            self.ch.basic_publish(msg, exchange=amqp.broadcast_exchange)
        except:
            raise VogelerServerException("Unable to publish message to the queue")

    def close(self):
        self.ch.close()

