from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='vogeler',
      version=version,
      description="Python-based CMDB",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='John E. Vincent',
      author_email='jvincent@tsys.com',
      url='http://10.32.4.43:9999/vogeler',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
