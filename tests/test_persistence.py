import unittest
import os, os.path

from uuid import uuid4

import vogeler.persistence as engine
from vogeler.exceptions import VogelerException

class CouchPersistenceTestCase(unittest.TestCase):

    def setUp(self):
        self.random_db_name = 'test_'+str(uuid4())
        self.conn = engine.create_engine("couch://127.0.0.1:5984/"+self.random_db_name)
        self.conn.create_db()

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
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
