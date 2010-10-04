import json

import vogeler.logger as logger
import vogeler.exceptions as exceptions

from vogeler.common import VogelerCommon

class VogelerClient(VogelerCommon):
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

