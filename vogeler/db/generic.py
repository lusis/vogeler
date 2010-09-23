import vogeler.db.couch as couch

class GenericPersistence(object):

    def __init__(self, scheme, dsn):
        self.scheme = scheme
        self.dsn = dsn

    def connect(self):
        engine = getattr(self, '_connect_%s' % self.scheme)
        return engine

    def connect_couch(self):
        engine = couch.VogelerStore(self.dsn)
        return engine
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
