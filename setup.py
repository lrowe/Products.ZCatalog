##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from setuptools import setup, find_packages

tests_require = ['zope.testing',
                 'plone.testing']

setup(name='Products.ZCatalog',
      version = '2.13.22dev',
      url='http://pypi.python.org/pypi/Products.ZCatalog',
      license='ZPL 2.1',
      description="Zope 2's indexing and search solution.",
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      packages=find_packages('src'),
      namespace_packages=['Products'],
      package_dir={'': 'src'},
      install_requires=[
        'setuptools',
        'AccessControl',
        'Acquisition',
        'DateTime',
        'DocumentTemplate',
        'ExtensionClass',
        'Missing',
        'Persistence',
        'Products.ZCTextIndex',
        'Record',
        'RestrictedPython',
        'zExceptions',
        'ZODB3',
        'Zope2',
        'zope.dottedname',
        'zope.interface',
        'zope.schema',
        'five.intid',
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require, },
      include_package_data=True,
      zip_safe=False,
      )
