import unittest
from vogeler.vogeler import VogelerClient, VogelerException

class ClientTestCase(unittest.TestCase):

    def assertType(self, obj, typ):
        self.assert_(type(obj)) is typ

    def echo(self, request):
        return request

    def test_vogeler_client_init(self):
        """Test that creating a Client object works"""
        c = VogelerClient(callback_function=self.echo,
                        host='localhost',
                        username='guest',
                        password='guest')
        self.assertType(c, 'vogeler.vogeler.VogelerClient')
        c.close()

    def test_vogeler_client_failure(self):
        """Test that Client object fails properly"""
        with self.assertRaises(VogelerException):
            VogelerClient(callback_function=self.echo,
                        host='10.10.10.2',
                        username='foobar',
                        password='baz')

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
