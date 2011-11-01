"""
Functional tests covering the catalog in a Zope2 stack.
"""

import unittest

import transaction

from plone import testing
from plone.testing import z2
from plone.testing import zodb

from Acquisition import aq_base
from OFS import Folder
from OFS import SimpleItem

from Products.ZCatalog import ZCatalog
from Products.PluginIndexes.FieldIndex import FieldIndex


class ZCatalogLayer(testing.Layer):
    defaultBases = (z2.FUNCTIONAL_TESTING,)
    
    def setUp(self):
        self['zodbDB'] = zodb.stackDemoStorage(
            self.get('zodbDB'), name='MyLayer')
        with z2.zopeApp() as app:
            ZCatalog.manage_addZCatalog(
                app, id='catalog', title='Catalog')
            self['app'] = app
            self['catalog'] = app['catalog']
        
    def tearDown(self):
        del self['catalog']
        del self['app']
        self['zodbDB'].close()
        del self['zodbDB']

ZCATALOG_FIXTURE = ZCatalogLayer()


class TestZCatalog(unittest.TestCase):

    layer = ZCATALOG_FIXTURE

    def setUp(self):
        self.app = self.layer['app']
        self.catalog = self.layer['catalog']
        id_ = FieldIndex.FieldIndex('id')
        self.catalog.addIndex('id', id_)

    def test_addAndCommit(self):
        """
        Test adding objects to the OFS, catalogging them and committing.

        Also test adding an object as a child of a folder before
        adding the folder to the DB.
        """
        # Create a folder and add an item to it before adding the
        # folder to the ZODB
        foo_folder = Folder.Folder('foo_folder')
        bar_item = SimpleItem.SimpleItem()
        bar_item.id = 'bar_item'
        foo_folder._setObject('bar_item', bar_item)
        bar_item = foo_folder['bar_item']

        # Add the folder to the ZODB and catalog both items
        self.app._setObject('foo_folder', foo_folder)
        foo_folder = self.app['foo_folder']
        self.catalog.catalog_object(foo_folder)
        self.catalog.catalog_object(bar_item)

        # Commit all the changes to this ZODB connection
        transaction.commit()

        # Query the catalog from the same ZODB connection
        # and check everything is working
        foo_brains = self.catalog(id=foo_folder.id)
        self.assertEqual(len(foo_brains), 1)
        bar_brains = self.catalog(id=bar_item.id)
        self.assertEqual(len(bar_brains), 1)
        self.assertTrue(aq_base(foo_brains[0].getObject())
                        is aq_base(foo_folder))
        self.assertTrue(aq_base(bar_brains[0].getObject())
                        is aq_base(bar_item))

        # Query the catalog from a new ZODB connection
        # and check everything is working
        with z2.zopeApp() as app:
            catalog = app['catalog']
            foo_brains = catalog(id=foo_folder.id)
            self.assertEqual(len(foo_brains), 1)
            bar_brains = catalog(id=bar_item.id)
            self.assertEqual(len(bar_brains), 1)
            self.assertEqual(foo_brains[0].getObject()._p_oid,
                             foo_folder._p_oid)
            self.assertEqual(bar_brains[0].getObject()._p_oid,
                             bar_item._p_oid)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestZCatalog))
    return suite
