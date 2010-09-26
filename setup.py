import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.9.2'

# Anyone know a better way to do python version conditionals in install_requires?
modules = ['amqplib', 'couchdbkit', 'pyyaml']

if sys.version_info < (2, 7):
    two_six = ['argparse', 'anyjson']
    modules.extend(two_six)

if __name__ == "__main__":

    setup(name='vogeler',
          version=version,
          description="Python-based CMDB Framework",
          long_description="Vogeler is a framework for building a configuration management system. It uses a modern communication framework built around message queues to get information from systems on demand.",
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
          url='http://lusis.github.com/vogeler',
          packages=[
            "vogeler",
            "vogeler.db",
            "vogeler.queue",
          ],
          install_requires=modules,
          scripts=[
            "scripts/vogeler-client",
            "scripts/vogeler-runner",
            "scripts/vogeler-server",
          ],
          data_files=[
            ('/tmp/vogeler',
                ['etc/vogeler/vogeler.conf'] ),
            ('/tmp/vogeler/plugins',
                ['etc/vogeler/plugins/facter.cfg', 'etc/vogeler/plugins/rpms.cfg', 'etc/vogeler/plugins/ps.cfg', 'etc/vogeler/plugins/ohai.cfg'] ),
            ("/tmp/vogeler/_design/system_records/views/all",
                ['etc/vogeler/_design/system_records/views/all/map.js'] ),
            ("/tmp/vogeler/_design/system_records/views/by_name",
                ['etc/vogeler/_design/system_records/views/by_name/map.js'] ),
            ("/tmp/vogeler/_design/system_records/views/packages_by_host",
                ['etc/vogeler/_design/system_records/views/packages_by_host/map.js'] )
            ],
          )
