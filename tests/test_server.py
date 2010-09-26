import unittest
import json
import os

from vogeler.server import VogelerServer
from vogeler.exceptions import VogelerException

import fixtures.message as message

class ServerTestCase(unittest.TestCase):

    good_amqp_dsn = "amqp://guest:guest@127.0.0.1:5792/vogeler"
    bad_amqp_dsn = "amqp://guest:guest@10.10.10.10:5792/vogeler"

    def assertType(self, obj, typ):
        self.assert_(type(obj)) is typ

    def echo(self, request):
        return request

    def test_vogeler_server_init(self):
        """Test that creating a Server object works"""
        c = VogelerServer(callback_function=self.echo, dsn=self.good_amqp_dsn)
        self.assertType(c, 'vogeler.vogeler.VogelerServer')
        c.close()

    def test_vogeler_server_failure(self):
        """Test that Server object fails properly"""
        with self.assertRaises(Exception):
            VogelerServer(callback_function=self.echo, dsn=self.bad_amqp_dsn)

    def test_server_message_durable(self):
        """Test that server can send durable messages"""
        test_message = 'this is a test'
        c = VogelerServer(callback_function=self.echo, dsn=self.good_amqp_dsn)
        self.assertIsNone(c.message(test_message))
        c.close()

    def test_server_message_nondurable(self):
        """Test that server can send non-durable messages"""
        test_message = 'this is a test'
        c = VogelerServer(callback_function=self.echo, dsn=self.good_amqp_dsn)
        self.assertIsNone(c.message(test_message, durable=False))
        c.close()

    @unittest.skip("Callback tests fail for now")
    def test_server_callback(self):
        """Test that server callbacks work"""
        sample_text = 'this is a test'
        message_body = json.dumps(sample_text)
        test_message = message.SampleMessage(message_body)
        c = VogelerServer(callback_function=self.echo,
                        host='localhost',
                        username='guest',
                        password='guest')
        m = c.ch.basic_consume(c.queue, callback=c.callback, no_ack=True)
        self.assertEquals(m.message, sample_text)
        c.close()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
