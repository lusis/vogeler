import json

import vogeler.log as logger
import vogeler.conf as conf
from vogeler.exceptions import VogelerRunnerException
from vogeler.messaging import amqp

log = logger.setup_logger(logLevel='DEBUG', logFile=None)

class VogelerRunner(object):
    """
    Base class for operating as a Vogeler runner instance

    :param str destination: routing_key to be used by the binding

    .. attribute:: ch

        an instance of :class:`amqplib.client_0_8.channel.Channel`

    .. attribute:: queue

        an instance of :class:`amqplib.client_0_8.channel.Queue`

    :raises: :class:`vogeler.exceptions.VogelerClientException`

    """
    def __init__(self, destination, **kwargs):
        try:
            self._configure(kwargs["config"])
            if self._config.has_option('amqp', 'dsn'):
                _dsn = self._config.get('amqp', 'dsn')
        except KeyError, e:
            _dsn = kwargs["dsn"]

        try:
            self.routing_key = destination
            self.ch = amqp.setup_amqp(_dsn)
            log.info("Vogeler(Runner) is starting up")
        except Exception, e:
            msg = "Unable to connect to broker %s" % _dsn
            log.fatal(msg)
            raise VogelerRunnerException(e)

    def _configure(self, config_file=None):
        if config_file is not None:
            self._config = conf.configure(cfg=config_file)

    def message(self, message, durable=True):
        """
        Method for sending a message via the messaging system

        :param message: The message to send.

        :param bool durable: Sets the durable flag on the message causing it to persists

        .. attribute:: msg

            instance of :class:`amqplib.client_0_8.basic_message.Message` wrapped in JSON

        """
        log.info("Vogeler(Runner) is sending a message")
        try:
            msg = amqp.amqp.Message(json.dumps(message))
            if durable == True:
                msg.properties['deliver_mode'] = 2
            self.ch.basic_publish(msg, exchange=amqp.broadcast_exchange, routing_key=self.routing_key)
        except:
            log.fatal("Error publishing message to the queue")
            raise VogelerRunnerException("Unable to publish message: %s" % message)

    def close(self):
        """Close the channel with the broker"""
        log.info("Closing channel")
        self.ch.close()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
