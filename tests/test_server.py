import unittest
from vogeler.vogeler import VogelerServer, VogelerException

class ServerTestCase(unittest.TestCase):

    def assertType(self, obj, typ):
        self.assert_(type(obj)) is typ

    def echo(self, request):
        return request

    def test_vogeler_server_init(self):
        """Test that creating a Server object works"""
        c = VogelerServer(callback_function=self.echo,
                        host='localhost',
                        username='guest',
                        password='guest')
        self.assertType(c, 'vogeler.vogeler.VogelerServer')
        c.close()

    def test_vogeler_server_failure(self):
        """Test that Server object fails properly"""
        with self.assertRaises(VogelerException):
            VogelerServer(callback_function=self.echo,
                        host='10.10.10.2',
                        username='foobar',
                        password='baz')

    def test_server_message_durable(self):
        """Test that server can send durable messages"""
        test_message = 'this is a test'
        c = VogelerServer(callback_function=self.echo,
                        host='localhost',
                        username='guest',
                        password='guest')
        self.assertIsNone(c.message(test_message))

    def test_server_message_nondurable(self):
        """Test that server can send non-durable messages"""
        test_message = 'this is a test'
        c = VogelerServer(callback_function=self.echo,
                        host='localhost',
                        username='guest',
                        password='guest')
        self.assertIsNone(c.message(test_message, durable=False))

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
