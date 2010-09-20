import datetime, yaml, json

import couchdbkit as couch
from couchdbkit.loaders import FileSystemDocsLoader

import vogeler.exceptions as exceptions
import vogeler.log as logger

log = logger.setup_logger(logLevel='DEBUG', logFile=None, name='vogeler-client')

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
            self.dbname = db
        except:
            raise

    def create_db(self, dbname=None):
        try:
            if not dbname:
                dbname = self.dbname

            self.db = self.server.get_or_create_db(dbname)
            SystemRecord.set_db(self.db)
        except:
            raise

    def drop_db(self, dbname=None):
        try:
            if not dbname:
                dbname = self.dbname

            self.server.delete_db(dbname)
        except:
            raise

    def use_db(self, dbname=None):
        try:
            if not dbname:
                dbname = self.dbname

            self.db = self.server.get_or_create_db(dbname)
            SystemRecord.set_db(self.db)
        except:
            raise

    def create(self, node_name):
        try:
            node = SystemRecord.get_or_create(node_name)
            node.system_name = node_name
            node.created_at = datetime.datetime.utcnow()
            node.save()
        except:
            raise

    def get(self, node_name):
        try:
            node = SystemRecord.get(node_name)
            self.node = node
            return node
        except:
            raise

    def touch(self, node_name):
        try:
            node = SystemRecord.get(node_name)
            node.updated_at = datetime.datetime.utcnow()
            node.save()
        except:
            raise

    def update(self, node_name, key, value, datatype):
        """Update a node record with a given key/value/datatype"""
        node = SystemRecord.get_or_create(node_name)

        try:
            datatype_method = getattr(self, '_update_%s' % datatype)
            node[key] = datatype_method(node, key, value)
        except AttributeError:
            log.warn("Don't know how to handle datatype: '%r'" % datatype)
            raise exceptions.VogelerPersistenceDataTypeException()

        node.updated_at = datetime.datetime.utcnow()
        node.save()

    def load_views(self, lp):
        self.loadpath = lp
        try:
            print "Loading design docs from %s" % lp
            loader = FileSystemDocsLoader(self.loadpath)
            loader.sync(self.db, verbose=True)
            print "Design docs loaded"
            return 0
        except:
            log.fatal("Document load path not found: %s" % lp)
            raise exceptions.VogelerPersistenceException()

    def _update_output(self, node, key, value):
        v = [z.strip() for z in value.split("\n")]
        return v

    def _update_json(self, node, key, value):
        return json.loads(value)

    def _update_pylist(self, node, key, value):
        return value

    def _update_pydict(self, node, key, value):
        return value

    def _update_yaml(self, node, key, value):
        return yaml.load(value)

    def _update_raw(self, node, key, value):
        return value

    def _update_string(self, node, key, value):
        return value
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
