import unittest

from vogeler.runner import VogelerRunner
from vogeler.exceptions import VogelerException


class RunnerTestCase(unittest.TestCase):

    good_amqp_dsn = "amqp://guest:guest@127.0.0.1:5792/vogeler"
    bad_amqp_dsn = "amqp://guest:guest@10.10.10.10:5792/vogeler"

    def assertType(self, obj, typ):
        self.assert_(type(obj)) is typ

    def echo(self, request):
        print request

    def test_vogeler_runner_init(self):
        """Test that creating a Runner object works"""
        c = VogelerRunner('broadcast.*', dsn=self.good_amqp_dsn)
        self.assertType(c, 'vogeler.vogeler.VogelerRunner')
        c.close()

    def test_vogeler_runner_failure(self):
        """Test that Runner object fails properly"""
        with self.assertRaises(VogelerException):
            VogelerRunner('broadcast.*', dsn=self.bad_amqp_dsn)

    def test_runner_message_durable(self):
        """Test that runner can send durable messages"""
        test_message = 'facter'
        c = VogelerRunner('broadcast.*', dsn=self.good_amqp_dsn)
        self.assertIsNone(c.message(test_message))
        c.close()

    def test_runner_message_nondurable(self):
        """Test that runner can send non-durable messages"""
        test_message = 'facter'
        c = VogelerRunner('broadcast.*', dsn=self.good_amqp_dsn)
        self.assertIsNone(c.message(test_message, durable=False))
        c.close()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
