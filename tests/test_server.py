import unittest
from vogeler.vogeler import VogelerServer

class ServerTestCase(unittest.TestCase):

    def assertType(self, obj, typ):
        self.assert_(type(obj)) is typ

    def echo(self, request):
        return request

    def test_vogeler_Server_init(self):
        """Test that creating a Server object works"""
        c = VogelerServer(callback_function=self.echo,
                        host='localhost',
                        username='guest',
                        password='guest')
        self.assertType(c, 'vogeler.vogeler.VogelerServer')
        c.close()
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
