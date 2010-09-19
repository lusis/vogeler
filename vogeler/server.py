import json

import vogeler.log as logger
from vogeler.exceptions import VogelerServerException
from vogeler.messaging import amqp

log = logger.setup_logger(logLevel='DEBUG', logFile=None, name='vogeler-server')

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
        try:
            self.ch, self.queue = amqp.setup_server(kwargs['host'], kwargs['username'], kwargs['password'])
            self.callback_function = callback_function
        except:
            raise VogelerServerException("Unable to connect to messaging system on %s as %s" % (kwargs['host'], kwargs['username']))

    def callback(self, msg):
        """
        Wrapper method for handling callbacks on message reciept.
        The message body is JSON decoded and passed up to :attr:`callback_function`

        :param msg: Instance of :class:`amqplib.client_0_8.basic_message.Message`

        """
        try:
            message = json.loads(msg.body)
        except:
            log.error("Message not in JSON format")

        if(self.callback_function):
            self.callback_function(message)

    def monitor(self):
        """
        Method for watching a queue infinitely for messages

        :raises: :class:`vogeler.exceptions.VogelerClientException`
        """
        try:
            log.info("Vogeler(Server) is starting up")
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
        except:
            log.fatal("Error Consuming queue")
            raise VogelerServerException("Error consuming queue")

        while self.ch.callbacks:
            self.ch.wait()

    def message(self, message, durable=True):
        """
        Method for sending a message via the messaging system

        :param message: The message to send.

        :param bool durable: Sets the durable flag on the message causing it to persists

        .. attribute:: msg

            instance of :class:`amqplib.client_0_8.basic_message.Message` wrapped in JSON

        """
        log.info("Vogeler(Server) is sending a message")
        try:
            msg = amqp.amqp.Message(json.dumps(message))
            if durable == True:
                msg.properties['delivery_mode'] = 2
            self.ch.basic_publish(msg, exchange=amqp.broadcast_exchange)
        except:
            log.fatal("Error publishing message to the queue")
            raise VogelerServerException("Unable to publish message to the queue")

    def close(self):
        """Close the channel with the broker"""
        self.ch.close()

