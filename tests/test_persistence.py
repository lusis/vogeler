import unittest
import os, os.path
import datetime as dt

from uuid import uuid4
from time import sleep

import vogeler.persistence as engine
from vogeler.exceptions import VogelerException

class CouchPersistenceTestCase(unittest.TestCase):

    def setUp(self):
        self.random_db_name = 'test_'+str(uuid4())
        self.conn = engine.create_engine("couch://127.0.0.1:5984/"+self.random_db_name)
        self.conn.create_db()
        self.conn.use_db()

    def tearDown(self):
        self.conn.drop_db()

    def test_filesystem_loader_valid(self):
        """Test that loading valid design docs works"""
        docpath = os.path.dirname(__file__)+"/fixtures/_design"
        results = self.conn.load_views(docpath)
        self.assertEquals(results, 0)

    def test_filesystem_load_invalid(self):
        """Test that loading from an invalid path works"""
        docpath = "/foo/bar/baz"
        with self.assertRaises(VogelerException):
            self.conn.load_views(docpath)

    def test_create_node(self):
        """Test that creating a node works"""
        doc_path = os.path.dirname(__file__)+"/fixtures/_design"
        self.conn.load_views(doc_path)
        nodename = 'node_'+str(uuid4())
        self.conn.create(nodename)
        n = self.conn.get(nodename)
        self.assertEquals(n.system_name, nodename)
        self.assertEquals(n.system_name, n._id)

    def test_touch_node(self):
        """Test that touching a node works"""
        nodename = 'node_'+str(uuid4())
        self.conn.create(nodename)
        sleep(7)
        self.conn.touch(nodename)
        n = self.conn.get(nodename)
        timediff = (n.updated_at - n.created_at) > dt.timedelta (seconds = 5)
        self.assertTrue(timediff)

    def test_update_node_output(self):
        """Test that updating a node with output datatype works"""
        nodename = 'node_'+str(uuid4())
        key, value = "packages", "package-1.0.4.rpm\npackage2-2.0.2.rpm"
        self.conn.update(nodename, key, value, 'output')
        n = self.conn.get(nodename)
        self.assertEqual("\n".join(n[key]), value)

    def test_update_node_pylist(self):
        """Test updating a node with pylist datatype works"""
        nodename = 'node_'+str(uuid4())
        key, value = "mylist", ['foo', 'bar', 'baz']
        self.conn.update(nodename, key, value, 'pylist')
        n = self.conn.get(nodename)
        self.assertListEqual(n[key], value)

    def test_update_node_pydict(self):
        """Test updating a node with pydict datatype works"""
        nodename = 'node_'+str(uuid4())
        key, value = "mydict", {'foo' : 1, 'bar' : 2, 'baz' : 'shoe'}
        self.conn.update(nodename, key, value, 'pydict')
        n = self.conn.get(nodename)
        self.assertDictEqual(n[key], value)

    def test_update_node_string(self):
        """Test updating a node with string datatype works"""
        nodename = 'node_'+str(uuid4())
        key, value = "mystring", "192.168.1.2"
        self.conn.update(nodename, key, value, 'string')
        n = self.conn.get(nodename)
        self.assertEqual(n[key], value)

    def test_update_node_raw(self):
        """Test updating a node with raw datatype works"""
        nodename = 'node_'+str(uuid4())
        key, value = "mystring", "192.168.1.2"
        self.conn.update(nodename, key, value, 'raw')
        n = self.conn.get(nodename)
        self.assertEqual(n[key], value)

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
