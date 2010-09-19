import unittest
import os, os.path
import re

from platform import node

from vogeler.plugins import VogelerPlugin
from vogeler.exceptions import VogelerException

class PluginTestCase(unittest.TestCase):

    def tearDown(self):
        if os.path.isfile('/tmp/vogeler-plugins.cfg') == True:
            os.remove('/tmp/vogeler-plugins.cfg')

    def assertType(self, obj, typ):
        self.assertTrue(type(obj)) is typ

    def assertFileContains(self, source, string):
        if os.path.isfile(source) == True:
            fh = open(source, 'r')
            file_contents = fh.read()
            p = re.compile(string)
            self.assertRegexpMatches(file_contents, p)

    def test_vogeler_plugin_init(self):
        """Test that creating a Plugin object works"""
        p = VogelerPlugin()
        self.assertType(p, 'vogeler.vogeler.VogelerPlugin')

    def test_vogeler_plugin_init_with_fixture(self):
        """Test that creating a Plugin object with a path works"""
        p = VogelerPlugin(plugin_dir=os.path.dirname(__file__)+'/fixtures/plugins/')
        self.assertType(p, 'vogeler.vogeler.VogelerPlugin')
        self.assertFileContains('/tmp/vogeler-plugins.cfg', 'facter')

    def test_execute_valid_plugin(self):
        """Test that execute plugin works properly"""
        p = VogelerPlugin(plugin_dir=os.path.dirname(__file__)+'/fixtures/plugins/')
        results = p.execute_plugin('facter')
        syskey_subset = {'syskey' : node()}
        format_subset = {'format' : 'yaml'}
        self.assertType(results, 'dict')
        self.assertDictContainsSubset(syskey_subset, results)
        self.assertDictContainsSubset(format_subset, results)

    @unittest.skip("Need to figure out how to parse stdout from Nose")
    def test_execute_unauth_plugin(self):
        """Test that execute does NOT work with an unauthorized plugin"""
        with self.assertRaises(VogelerException):
            p = VogelerPlugin()
            p.execute_plugin('invalid')

    @unittest.skip("Need to figure out how to parse stdout from Nose")
    def test_execute_failing_plugin(self):
        """Test that execute does NOT work with a broken plugin"""
        with self.assertRaises(VogelerException):
            p = VogelerPlugin(plugin_dir=os.path.dirname(__file__)+'/fixtures/plugins/')
            p.execute_plugin('broken')

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
