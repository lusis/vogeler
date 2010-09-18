import json

import vogeler.log as logger
from vogeler.exceptions import VogelerRunnerException
from vogeler.messaging import amqp

log = logger.setup_logger(logLevel='DEBUG', logFile=None, name='vogeler-runner')

class VogelerRunner(object):
    def __init__(self, destination, **kwargs):
        try:
            self.routing_key = destination
            self.ch = amqp.setup_amqp(kwargs['host'], kwargs['username'], kwargs['password'])
            log.info("Vogeler(Runner) is starting up")
        except:
            raise VogelerRunnerException("Unable to connect to %s as %s" % (kwargs['host'], kwargs['username']) )

    def message(self, message, durable=True):
        log.info("Vogeler(Runner) is sending a message")
        try:
            msg = amqp.amqp.Message(json.dumps(message))
            if durable == True:
                msg.properties['deliver_mode'] = 2
            self.ch.basic_publish(msg, exchange=amqp.broadcast_exchange, routing_key=self.routing_key)
        except:
            raise VogelerRunnerException("Unable to publish message: %s" % message)

    def close(self):
        log.info("Closing channel")
        self.ch.close()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
