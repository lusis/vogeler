from distutils.core import setup

version = '0.2'

if __name__ == "__main__":

    setup(name='vogeler',
          version=version,
          description="Python-based CMDB",
          long_description="""User-extendable CMDB based on Python, RabbitMQ and CouchDB""",
          classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: GNU General Public License (GPL)',
              'Natural Language :: English',
              'Programming Language :: Python :: 2.7',
              'Topic :: Software Development :: Libraries :: Python Modules',
          ],
          keywords='cmdb',
          author='John E. Vincent',
          author_email='lusis.org+github.com@gmail.com',
          url='http://github.com/lusis/vogeler',
          packages=[
            "vogeler",
          ],
          install_requires=['pyyaml','amqplib', 'couchdbkit'],
          scripts=[
            "scripts/vogeler-client",
            "scripts/vogeler-runner",
            "scripts/vogeler-server",
          ],
          data_files=[
            ("etc/vogeler/plugins", ['etc/plugins/facter.cfg', 'etc/plugins/rpms.cfg']),
            ("etc/vogeler/_design/system_records/views/all", ['etc/_design/system_records/views/all/map.js']),
            ("etc/vogeler/_design/system_records/views/by_name", ['etc/_design/system_records/views/by_name/map.js']),
            ("etc/vogeler/_design/system_records/views/packages_by_host", ['etc/_design/system_records/views/packages_by_host/map.js'])
            ]
          )
