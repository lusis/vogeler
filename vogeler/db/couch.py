import datetime
import couchdbkit as couch
from couchdbkit.loaders import FileSystemDocsLoader

import vogeler.exceptions as exceptions
import vogeler.logger as logger

from vogeler.db.generic import GenericPersistence

log = logger.LogWrapper(name='vogeler.db.couch').logger()

class SystemRecord(couch.Document):
    """
    A couchdbkit document for storing our base information
    All documents, regardless of backend, should support
    the following fields:
    system_name
    created_at
    updated_at
    """
    system_name = couch.StringProperty()
    created_at = couch.DateTimeProperty()
    updated_at = couch.DateTimeProperty()

class Persistence(GenericPersistence):

    def hook_connect(self, **kwargs):
        if self.username is None or self.password is None:
            connection_string = "http://%s:%s" % (self.host, self.port)
        else:
            connection_string = "http://%s:%s@%s:%s" % (self.username, self.password, self.host, self.port)
        self._server = couch.Server(uri=connection_string)

    def hook_createdb(self, dbname):
        try:
            self.db = self._server.get_or_create_db(dbname)
            SystemRecord.set_db(self.db)
        except:
            raise

    def hook_dropdb(self, dbname):
        try:
            self._server.delete_db(dbname)
        except:
            raise

    def hook_usedb(self, dbname):
        try:
            self.db = self._server.get_or_create_db(dbname)
            SystemRecord.set_db(self.db)
        except:
            raise

    def hook_create(self, node_name):
        try:
            node = SystemRecord.get_or_create(node_name)
            node.system_name = node_name
            node.created_at = datetime.datetime.utcnow()
            node.save()
        except:
            raise

    def hook_get(self, node_name):
        try:
            node = SystemRecord.get(node_name)
            self.node = node
            return node
        except:
            raise

    def hook_touch(self, node_name):
        try:
            node = SystemRecord.get(node_name)
            node.updated_at = datetime.datetime.utcnow()
            node.save()
        except:
            raise


    def hook_update(self, node_name, key, value):
        try:
            node = SystemRecord.get_or_create(node_name)
            node[key] = value
            node.updated_at = datetime.datetime.utcnow()
            node.save()
        except:
            raise

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

class VogelerCouchPersistenceException(exceptions.VogelerPersistenceException): pass
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
