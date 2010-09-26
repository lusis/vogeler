import json

import vogeler.logger as logger
import vogeler.exceptions as exceptions
import vogeler.conf as conf
from vogeler.messaging import amqp


class VogelerClient(object):
    """
    Base class for operating as a Vogeler client instance

    :param none callback_function: Callback function to use when messages are recieved

    .. attribute:: callback_function

        External callback used for processing messages

    .. attribute:: ch

        an instance of :class:`amqplib.client_0_8.channel.Channel`

    .. attribute:: queue

        an instance of :class:`amqplib.client_0_8.channel.Queue`

    :raises: :class:`vogeler.exceptions.VogelerClientConnectionException`

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

        self.log = logger.LogWrapper(name='vogeler-client', level=log_level).logger()

        if kwargs.has_key("dsn"):
            _dsn = kwargs["dsn"]
        elif self._configured is True and self._config.has_option('amqp', 'dsn'):
            _dsn = self._config.get('amqp', 'dsn')
        else:
            self.log.fatal("No dsn provided. Cannot continue")

        try:
            self.ch, self.queue = amqp.setup_client(_dsn)
            self.callback_function = callback_function
        except Exception, e:
            self.log.fatal("Error connecting to %s" % _dsn)
            raise exceptions.VogelerClientConnectionException(e)

    def _configure(self, config_file=None):
        if config_file is not None:
            self._config = conf.configure(cfg=config_file)

    def callback(self, msg):
        """
        Wrapper method for handling callbacks on message reciept.
        The message body is JSON decoded and passed up to :attr:`callback_function`

        :param msg: Instance of :class:`amqplib.client_0_8.basic_message.Message`

        """
        self.log.info("Message recieved")
        try:
            message = json.loads(msg.body)
            self.log.info("Message decoded")
        except Exception, e:
            self.log.warn("Message not in JSON format")
            raise exceptions.VogelerClientPluginException(e)

        if(self.callback_function):
            self.callback_function(message)

    def monitor(self):
        """
        Method for watching a queue infinitely for messages

        :raises: :class:`vogeler.exceptions.VogelerClientException`
        """
        try:
            self.log.info("Vogeler(Client) is starting up")
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
            self.log.info("Vogeler(Client) has started")
        except Exception, e:
            self.log.fatal("Error Consuming queue")
            raise exceptions.VogelerClientConnectionException(e)

        while self.ch.callbacks:
            self.ch.wait()

    def message(self, message, durable=True):
        """
        Method for sending a message via the messaging system

        :param message: The message to send.

        :param bool durable: Sets the durable flag on the message causing it to persists

        .. attribute:: msg

            instance of :class:`amqplib.client_0_8.basic_message.Message` wrapped in JSON

        :raises: :class:`vogeler.exceptions.VogelerClientException`

        """
        try:
            self.log.debug("Vogeler(Client) is sending a message")
            msg = amqp.amqp.Message(json.dumps(message))
            if durable == True:
                msg.properties['delivery_mode'] = 2
            self.ch.basic_publish(msg, exchange=amqp.master_exchange)
            self.log.debug("Vogeler(Client) finished sending message")
        except Exception, e:
            self.log.fatal("Error publishing message to the queue")
            raise exceptions.VogelerClientConnectionException(e)

    def close(self):
        """Close the channel with the broker"""
        self.log.info("Closing channel")
        self.ch.close()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
