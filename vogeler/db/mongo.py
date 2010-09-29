import datetime
import pymongo as mongo

import vogeler.exceptions as exceptions
import vogeler.logger as logger

from vogeler.db.generic import GenericPersistence

log = logger.LogWrapper(name='vogeler.db.mongo').logger()

class Persistence(GenericPersistence):
    """
    The format for mongodb backends uses the following model:
    database name from param
    collection name - databasename_collection

    Will consider better options ;)

    Also, all inserts/saves are done with safe=True
    """

    def hook_connect(self, **kwargs):
        if self.username is None or self.password is None:
            connection_string = "mongodb://%s:%s" % (self.host, self.port)
        else:
            connection_string = "mongodb://%s:%s@%s:%s" % (self.username, self.password, self.host, self.port)
        self._server = mongo.Connection(host=connection_string)

    def hook_createdb(self, dbname):
        """
        mongodb does lazy creation for databases and collections.
        We'll use space to go ahead and define our collection and return it
        All operations are on the collection anyway as opposed to the database
        """
        try:
            _collection = "%s_collection" % dbname
            """
            self.db is a bit of a misnomer since we operate on the collection
            We'll just do it all in one shot here
            The following is essentially the same as
            >>> database = self._server['vogeler']
            >>> self.db = database['vogeler_collection']
            self.db is now a reference to the collection
            """
            self.db = eval("self._server['%s']['%s']" % (dbname, _collection))
        except:
            raise

    def hook_dropdb(self, dbname):
        try:
            self._server.drop_database(dbname)
        except:
            raise

    def hook_usedb(self, dbname):
        """eliminate error and just call createdb"""
        self.hook_createdb(dbname)

    def hook_create(self, node_name):
        """Reminder: We operate on the collection in mongodb, not the database"""
        try:
            _collection = self.db
            node = { '_id': node_name,
                     'system_name': node_name,
                     'created_at': datetime.datetime.utcnow()}
            _collection.save(node, safe=True)
        except:
            raise

    def hook_get(self, node_name):
        try:
            _params = {"_id": node_name}
            _collection = self.db
            node = _collection.find_one(_params)
            self.node = node
            return node
        except:
            raise

    def hook_touch(self, node_name):
        """
        We use don't use upsert here because we can't guarantee that "created_at" is populated
        We use $set to update the single value
        """
        try:
            _params = {"$set": {"updated_at": datetime.datetime.utcnow()}}
            node = self.hook_get(node_name)
            _collection = self.db
            _collection.update(node, _params, safe=True)
        except:
            raise

    def hook_update(self, node_name, key, value):
        """
        We use don't use upsert here because we can't guarantee that "created_at" is populated
        We use $set to update the single value
        """
        try:
            _params = {"$set": {key: value, "updated_at": datetime.datetime.utcnow()}}
            node = self.hook_get(node_name)
            _collection = self.db
            _collection.update(node, _params, safe=True)
        except:
            raise

class VogelerMongoPersistenceException(exceptions.VogelerPersistenceException): pass
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
