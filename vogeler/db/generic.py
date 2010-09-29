import urlparse, json, yaml, datetime

import vogeler.logger as logger
import vogeler.exceptions as exceptions

log = logger.LogWrapper(name='vogeler.db').logger()

class GenericPersistence(object):

    def __init__(self, dsn, **kwargs):
        try:
            _parsed = urlparse.urlparse(dsn)
            self.username, self.password = _parsed.username, _parsed.password
            self.host, self.port = _parsed.hostname, _parsed.port

            db = _parsed.path.split("/")[1]
            if self.host is None or self.port is None:
                log.fatal("Invalid DSN provided: %s" % dsn)
            if db is None:
                log.fatal("Invalid DSN provided: %s" % dsn)
        except:
            raise

        self.dbname = db
        self.connect()

    def connect(self, **kwargs):
        """
        Method for connection to a server
        """
        self.hook_connect(**kwargs)

    def hook_connect(self, **kwargs):
        """You should override this method"""
        pass

    def create_db(self, dbname=None):
        """
        Method for creating a database
        Should gracefully handle existing databases
        """
        try:
            if dbname is None:
                dbname = self.dbname
            else:
                self.dbname = dbname

            self.hook_createdb(dbname)
        except:
            raise

    def hook_createdb(self, dbname):
        """You should override this method"""
        pass

    def drop_db(self, dbname=None):
        """
        Method for dropping a database
        """
        try:
            if dbname is None:
                dbname = self.dbname
            else:
                self.dbname = dbname

            self.hook_dropdb(dbname)
        except:
            raise

    def hook_dropdb(self, dbname):
        """You should override this method"""
        pass

    def use_db(self, dbname=None):
        """
        Helper method for using a database
        """
        try:
            if dbname is None:
                dbname = self.dbname
            else:
                self.dbname = dbname
            self.hook_usedb(dbname)
        except:
            raise

    def hook_usedb(self, dbname):
        """You should override this method"""
        pass

    def create(self, node_name):
        """Method for getting a node's record"""
        try:
            self.hook_create(node_name)
        except:
            raise

    def hook_create(self, node_name):
        """You should override this method"""
        pass

    def get(self, node_name):
        """Method for getting a node's record"""
        try:
            node = self.hook_get(node_name)
            self.node = node_name
            return node
        except:
            raise

    def hook_get(self, node_name):
        """You should override this method"""
        pass

    def touch(self, node_name):
        """Convenience method for updating a node's timestamp"""
        try:
            self.hook_touch(node_name)
        except:
            raise

    def hook_touch(self, node_name):
        """You should override this method"""
        pass

    def update(self, node_name, key, value, datatype):
        """Update a node record with the given key/value/datatype"""

        try:
            datatype_method = getattr(self, '_update_%s' % datatype)
            data = datatype_method(node_name, key, value)
            self.hook_update(node_name, key, data)
        except AttributeError:
            log.warn("Don't know how to handle datatype: '%r'" % datatype)
            raise exceptions.VogelerPersistenceDataTypeException()

    def hook_update(self, node_name, key, value):
        """You should override this method"""
        pass

    """
    Do not mess with the following methods.
    All the logic is handled here for you.
    Just be ready to accept each of these datatypes
    """
    def _update_output(self, node, key, value):
        """ process output handler. split at newlines """
        v = [z.strip() for z in value.split("\n")]
        return v

    def _update_json(self, node, key, value):
        """ json handler. load json and persist """
        return json.loads(value)

    def _update_pylist(self, node, key, value):
        """ python list datatype handler """
        return value

    def _update_pydict(self, node, key, value):
        """ python dictionary datatype handler """
        return value

    def _update_yaml(self, node, key, value):
        """ yaml datatype handler. load yaml and persist """
        return yaml.load(value)

    def _update_raw(self, node, key, value):
        """ raw datatype handler """
        return value

    def _update_string(self, node, key, value):
        """ simple value handler """
        return value

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
