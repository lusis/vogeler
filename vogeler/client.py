import json

import vogeler.log as logger
from vogeler.exceptions import VogelerClientException
from vogeler.messaging import amqp

log = logger.setup_logger(logLevel='DEBUG', logFile=None, name='vogeler-client')

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

    :raises: :class:`vogeler.exceptions.VogelerClientException`


    """
    def __init__(self, callback_function=None, **kwargs):
        try:
            self.ch, self.queue = amqp.setup_client(kwargs['host'], kwargs['username'], kwargs['password'])
            self.callback_function = callback_function
        except:
            raise VogelerClientException("\
                    Error connecting to %s as %s" % (kwargs['host'], kwargs['username']))

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
            log.info("Vogeler(Client) is starting up")
            self.ch.basic_consume(self.queue, callback=self.callback, no_ack=True)
        except:
            log.fatal("Error Consuming queue")
            raise VogelerClientException("Error consuming queue")

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
        log.info("Vogeler(Client) is sending a message")
        msg = amqp.amqp.Message(json.dumps(message))
        if durable == True:
            msg.properties['delivery_mode'] = 2
        try:
            self.ch.basic_publish(msg, exchange=amqp.master_exchange)
        except:
            raise VogelerClientException("Error publishing message to queue")

    def close(self):
        """Close the channel with the broker"""
        self.ch.close()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
