import json

import vogeler.logger as logger
import vogeler.conf as conf
from vogeler.exceptions import VogelerServerException
from vogeler.messaging import amqp


class VogelerServer(object):
    """
    Base class for operating as a Vogeler server instance

    :param none callback_function: Callback function to use when messages are recieved

    .. attribute:: callback_function

        External callback used for processing messages

    .. attribute:: ch

        An instance of :class:`amqplib.client_0_8.channel.Channel`

    .. attribute:: queue

        An instance of :class:`amqplib.client_0_8.channel.Queue`

    :raises: :class:`vogeler.exceptions.VogelerServerException`

    """
    def __init__(self, callback_function=None, **kwargs):
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

        self.log = logger.LogWrapper(name='vogeler-server', level=log_level).logger()

        if kwargs.has_key("dsn"):
            _dsn = kwargs["dsn"]
        elif self._configured is True and self._config.has_option('amqp', 'dsn'):
            _dsn = self._config.get('amqp', 'dsn')
        else:
            self.log.fatal("No dsn provided. Cannot continue")

        try:
            self.ch, self.queue = amqp.setup_server(_dsn)
            self.callback_function = callback_function
        except Exception, e:
            raise e

    def _configure(self, config_file=None):
        if config_file is not None:
            self._config = conf.configure(cfg=config_file)
            self._configured = True

    def callback(self, msg):
        """
        Wrapper method for handling callbacks on message reciept.
        The message body is JSON decoded and passed up to :attr:`callback_function`

        :param msg: Instance of :class:`amqplib.client_0_8.basic_message.Message`

        """
        try:
            message = json.loads(msg.body)
        except Exception, e:
            self.log.error("Message not in JSON format: %s" % e)

        if(self.callback_function):
            self.callback_function(message)

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
            raise VogelerServerException(e)

        while self.ch.callbacks:
            self.log.info("Waiting for more messages")
            self.ch.wait()

    def message(self, message, durable=True):
        """
        Method for sending a message via the messaging system

        :param message: The message to send.

        :param bool durable: Sets the durable flag on the message causing it to persists

        .. attribute:: msg

            instance of :class:`amqplib.client_0_8.basic_message.Message` wrapped in JSON

        """
        self.log.info("Vogeler(Server) is sending a message")
        try:
            msg = amqp.amqp.Message(json.dumps(message))
            if durable == True:
                msg.properties['delivery_mode'] = 2
            self.ch.basic_publish(msg, exchange=amqp.broadcast_exchange)
        except Exception, e:
            self.log.fatal("Error publishing message to the queue")
            raise VogelerServerException(e)

    def close(self):
        """Close the channel with the broker"""
        self.ch.close()

