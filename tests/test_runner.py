import unittest
import json

from vogeler.vogeler import VogelerRunner, VogelerException
import fixtures.message as message

class RunnerTestCase(unittest.TestCase):

    def assertType(self, obj, typ):
        self.assert_(type(obj)) is typ

    def echo(self, request):
        print request

    def test_vogeler_runner_init(self):
        """Test that creating a Runner object works"""
        c = VogelerRunner('broadcast.*',
                        host='localhost',
                        username='guest',
                        password='guest')
        self.assertType(c, 'vogeler.vogeler.VogelerRunner')
        c.close()

    def test_vogeler_runner_failure(self):
        """Test that Runner object fails properly"""
        with self.assertRaises(VogelerException):
            VogelerRunner('broadcast.*',
                        host='10.10.10.2',
                        username='foobar',
                        password='baz')

    def test_runner_message_durable(self):
        """Test that runner can send durable messages"""
        test_message = 'facter'
        c = VogelerRunner('broadcast.*',
                        host='localhost',
                        username='guest',
                        password='guest')
        self.assertIsNone(c.message(test_message))
        c.close()

    def test_runner_message_nondurable(self):
        """Test that runner can send non-durable messages"""
        test_message = 'facter'
        c = VogelerRunner('broadcast.*',
                        host='localhost',
                        username='guest',
                        password='guest')
        self.assertIsNone(c.message(test_message, durable=False))
        c.close()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
