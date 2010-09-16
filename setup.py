import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.8'

# Anyone know a better way to do python version conditionals in install_requires?
modules = ['amqplib', 'couchdbkit', 'pyyaml']
if sys.version_info < (2, 7):
    two_six = ['argparse', 'anyjson']
    modules.extend(two_six)

if __name__ == "__main__":

    setup(name='vogeler',
          version=version,
          description="Python-based CMDB",
          long_description="""User-extendable CMDB based on Python, RabbitMQ and CouchDB""",
          classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Intended Audience :: System Administrators',
              'License :: OSI Approved :: GNU General Public License (GPL)',
              'Natural Language :: English',
              'Programming Language :: Python :: 2.6',
              'Programming Language :: Python :: 2.7',
              'Topic :: System :: Systems Administration',
              'Operating System :: POSIX :: Linux',
          ],
          keywords='cmdb',
          author='John E. Vincent',
          author_email='lusis.org+github.com@gmail.com',
          url='http://github.com/lusis/vogeler',
          packages=[
            "vogeler",
          ],
          install_requires=modules,
          scripts=[
            "scripts/vogeler-client",
            "scripts/vogeler-runner",
            "scripts/vogeler-server",
          ],
          data_files=[
            ("etc/vogeler/plugins", ['etc/plugins/facter.cfg', 'etc/plugins/rpms.cfg', 'etc/plugins/ps.cfg']),
            ("etc/vogeler/_design/system_records/views/all", ['etc/_design/system_records/views/all/map.js']),
            ("etc/vogeler/_design/system_records/views/by_name", ['etc/_design/system_records/views/by_name/map.js']),
            ("etc/vogeler/_design/system_records/views/packages_by_host", ['etc/_design/system_records/views/packages_by_host/map.js'])
            ]
          )
