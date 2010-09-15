import urlparse
import vogeler.db.couch as couch

from vogeler.exceptions import VogelerException

"""vogeler.persisistence is used like so:

import vogeler.persistence as engine
# Create or find and then use the system_records db
c = engine.create_engine('couch://127.0.0.1:5984/system_records')
# create or find the nodename node
c.create('nodename')
# update the nodename node with the given attributes
package_list = some_shell_command_output
c.update('nodename', 'packages', package_list', 'output')
mylist = ['foo','bar','baz']
c.update('nodename', 'my_python_list', mylist, 'pylist')
mydict = {'foo' : 1, 'bar' : 2, 'baz' : 'shoe'}
c.update('nodename', 'my_python_dict', mydict, 'pydict')
myyaml = some_yaml_data
c.update('nodename', 'my_yaml_data', myyaml, 'yaml')
c.update('nodename', 'my_string', 'some sting data', 'string')
myxml = some_xml_data
c.update('nodename', 'my_raw_data', myxml, 'raw')
"""
def create_engine(dsn, **credentials):
    try:
        scheme, params = _parse_url(dsn)
        connect_string = "%s.VogelerStore(%s)" % (scheme, params)
        engine = eval(connect_string)
        return engine
    except:
        #raise VogelerException()
        raise

def _parse_url(url):
    parsed = urlparse.urlparse(url)
    s = parsed.scheme
    h, p = parsed.netloc.split(':')
    d = parsed.path.split("/")[1]
    params = "host='%s', port='%s', db='%s'" % (h, p, d)
    return (s, params)

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
