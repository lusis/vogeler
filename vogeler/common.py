import json

import vogeler.logger as logger
import vogeler.conf as conf
import vogeler.exceptions as exceptions

from vogeler.messaging import amqp

class VogelerCommon(object):
    """
    Base class for operating in a Vogeler role
    """

    def __init__(self, callback_function=None, role='client', **kwargs):

        self._configured = False
        self.role = role

        if kwargs.has_key("config"):
            self._configure(kwargs["config"])
            self._configured = True

        if kwargs.has_key("loglevel"):
            log_level = kwargs["loglevel"]
        elif self._configured is True and self._config.has_option('global', 'log_level'):
            log_level = self._config.get('global', 'log_level')
        else:
            log_level = 'WARN'

        self.log = logger.LogWrapper(name='vogeler-%s' % self.role).logger()

        if kwargs.has_key("dsn"):
            _dsn = kwargs["dsn"]
        elif self._configured is True and self._config.has_option('amqp', 'dsn'):
            _dsn = self._config.get('amqp', 'dsn')
        else:
            error = "No dsn provided. Cannot continue"
            self.log.fatal(error)
            raise exceptions.VogelerMessagingException(error)

        try:
            self.ch, self.queue = amqp.setup_server(_dsn)
            self.callback_function = callback_function
        except Exception, e:
            error = "Error connecting to %s" % _dsn
            self.log.fatal(error)
            raise e

    def _configure(self, config_file=None):
        if config_file is not None:
            self._config = conf.configure(cfg=config_file)
            self._configured = True

    def message(self, message, durable=True):
        """
        Method for sending a message via the messaging system

        :param message: The message to send.

        :param bool durable: Sets the durable flag on the message causing it to persists

        .. attribute:: msg

            instance of :class:`amqplib.client_0_8.basic_message.Message` wrapped in JSON

        :raises: :class:`vogeler.exceptions.VogelerClientException`

        """
        if self.role == 'server':
            _exchange = amqp.broadcast_exchange
        elif self.role == 'client':
            _exchange = amqp.master_exchange
        else:
            _exchange = amqp.master_exchange

        try:
            self.log.info("Vogeler(%s) is sending a message" % self.role)
            msg = amqp.amqp.Message(json.dumps(message))
            if durable == True:
                msg.properties['delivery_mode'] = 2
            self.ch.basic_publish(msg, exchange=_exchange)
            self.log.info("Vogeler(%s) finished sending message" % self.role)
        except Exception, e:
            error = "Error publishing message to the queue"
            self.log.fatal(error)
            raise e

    def callback(self):
        """This should be overridden"""
        pass

    def monitor(self):
        """
        Method for watching a queue infinitely for messages

        :raises: :class:`vogeler.exceptions.VogelerClientException`
        """
        try:
            self.log.debug("Vogeler(Server) is starting up")
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
            self.log.info("Vogler(Server) has started")
        except Exception, e:
            self.log.fatal("Error Consuming queue")
            raise exceptions.VogelerMessagingException(e)

        while self.ch.callbacks:
            self.log.info("Waiting for more messages")
            self.ch.wait()

    def close(self):
        """Close the channel with the broker"""
        self.log.info("Closing channel")
        self.ch.close()
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
