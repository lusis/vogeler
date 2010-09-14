import couchdbkit as couch

from couchdbkit.loaders import FileSystemDocsLoader

from vogeler.exceptions import VogelerException

class SystemRecord(couch.Document):
    system_name = couch.StringProperty()
    updated_at = couch.DateTimeProperty()

def load(lp, database):
    try:
        print "Loading design docs from %s" % lp
        loader = FileSystemDocsLoader(lp)
        loader.sync(database, verbose=True)
        print "Design docs loaded"
        return 0
    except:
        raise VogelerException()
        return 1

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
