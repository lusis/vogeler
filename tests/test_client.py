import unittest
import json

from vogeler.client import VogelerClient
from vogeler.exceptions import VogelerException

import fixtures.message as message

class ClientTestCase(unittest.TestCase):

    good_amqp_dsn = "amqp://guest:guest@127.0.0.1:5792/vogeler"
    bad_amqp_dsn = "amqp://guest:guest@10.10.10.10:5792/vogeler"

    def assertType(self, obj, typ):
        self.assert_(type(obj)) is typ

    def echo(self, request):
        print request

    def test_vogeler_client_init(self):
        """Test that creating a Client object works"""
        c = VogelerClient(callback_function=self.echo, role='client', dsn=self.good_amqp_dsn)
        self.assertType(c, 'vogeler.vogeler.VogelerClient')
        c.close()

    def test_vogeler_client_failure(self):
        """Test that Client object fails properly"""
        with self.assertRaises(Exception):
            VogelerClient(callback_function=self.echo, role='client', dsn=self.bad_amqp_dsn)

    def test_client_message_durable(self):
        """Test that client can send durable messages"""
        test_message = 'this is a test'
        c = VogelerClient(callback_function=self.echo, role='client', dsn=self.good_amqp_dsn)
        self.assertIsNone(c.message(test_message))
        c.close()

    def test_client_message_nondurable(self):
        """Test that client can send non-durable messages"""
        test_message = 'this is a test'
        c = VogelerClient(callback_function=self.echo, role='client', dsn=self.good_amqp_dsn)
        self.assertIsNone(c.message(test_message, durable=False))
        c.close()

    @unittest.skip("Callback tests fail for now")
    def test_client_callback(self):
        """Test that client callbacks work"""
        sample_text = 'this is a test'
        message_body = json.dumps(sample_text)
        test_message = message.SampleMessage(message_body)
        c = VogelerClient(callback_function=None,
                        role='client',
                        host='localhost',
                        username='guest',
                        password='guest')
        m = c.callback(test_message)
        self.assertEquals(m.message, sample_text)
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
