import unittest
import os, os.path

from vogeler.persistence import couch
from vogeler.exceptions import VogelerException

class CouchPersistenceTestCase(unittest.TestCase):

    def test_filesystem_loader_valid(self):
        """Test that loading valid design docs works"""
        docpath = os.path.dirname(__file__)+"/fixtures/_design"
        database = "vogeler_test_docs"
        results = couch.load(docpath, database)
        self.assertEquals(results, 0)

    def test_filesystem_load_invalid(self):
        """Test that loading from an invalid path works"""
        docpath = "/foo/bar/baz"
        database = "vogeler_test_docs"
        with self.assertRaises(VogelerException):
            couch.load(docpath, database)
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
