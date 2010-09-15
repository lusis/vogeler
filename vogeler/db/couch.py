import datetime, yaml

import couchdbkit as couch
from couchdbkit.loaders import FileSystemDocsLoader

from vogeler.exceptions import VogelerException

class SystemRecord(couch.Document):
    system_name = couch.StringProperty()
    created_at = couch.DateTimeProperty()
    updated_at = couch.DateTimeProperty()

class VogelerStore(object):

    def __init__(self, **kwargs):
        try:
            host, port = kwargs['host'], kwargs['port']
            db = kwargs['db']
            connection_string = "http://%s:%s" % (host, port)
            self.server = couch.Server(uri=connection_string)
            self.create_db(db)
            self.use_db(db)
        except:
            raise
            #raise VogelerException()

    def create_db(self, dbname):
        try:
            self.db = self.server.get_or_create_db(dbname)
            SystemRecord.set_db(self.db)
        except:
            raise VogelerException()

    def use_db(self, dbname):
        try:
            self.db = self.server.get_or_create_db(dbname)
            SystemRecord.set_db(self.db)
        except:
            raise VogelerException()

    def create(self, node_name):
        node = SystemRecord.get_or_create(node_name)
        try:
            node.system_name = node_name
            node.created_at = datetime.datetime.utcnow()
            node.save()
        except:
            raise VogelerException()

    def touch(self, node_name):
        node = SystemRecord.get_or_create(node_name)
        try:
            node.updated_at = datetime.datetime.utcnow()
            node.save()
        except:
            raise VogelerException()

    def update(self, node_name, key, value, datatype):
        node = SystemRecord.get_or_create(node_name)

        if datatype == 'output':
            v = [z.strip() for z in value.split("\n")]
            node[key] = v
        if datatype == 'pylist':
            v = value
            node[key] = v
        if datatype == 'pydict':
            v = value
            node[key] = v
        if datatype == 'yaml':
            v = yaml.load(value)
            node[key] = v
        if datatype == 'string':
            v = value
            node[key] = v
        if datatype == 'raw':
            v = value
            node[key] = v
        node.updated_at = datetime.datetime.utcnow()
        node.save()

    def load_views(self, lp):
        self.loadpath = lp
        try:
            print "Loading design docs from %s" % lp
            loader = FileSystemDocsLoader(self.loadpath)
            loader.sync(self.db, verbose=True)
            print "Design docs loaded"
        except:
            raise VogelerException()

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
