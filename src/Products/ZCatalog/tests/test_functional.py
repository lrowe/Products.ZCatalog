"""
Functional tests covering the catalog in a Zope2 stack.
"""

import unittest

import transaction
from zope import component
from zope import intid
from zope.configuration import xmlconfig

from plone.testing import z2

from Acquisition import aq_base
from OFS import Folder
from OFS import SimpleItem
from Products.Five.component import browser
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import SpecialUsers

import five.intid
from Products.ZCatalog import ZCatalog
from Products.PluginIndexes.FieldIndex import FieldIndex


class ZCatalogLayer(z2.FunctionalTesting):
    defaultBases = (z2.FUNCTIONAL_TESTING,)
    
    def setUp(self):
        with z2.zopeApp() as app:

            # Set up intids
            xmlconfig.file('overrides.zcml', package=five.intid,
                           context=self['configurationContext'])
            browser.ObjectManagerSiteView(app, None).makeSite()
            sm = app.getSiteManager()
            sm.registerUtility(intid.IntIds(), intid.IIntIds)

            # Add a catalog and index
            ZCatalog.manage_addZCatalog(
                app, id='catalog', title='Catalog')
            catalog = app['catalog']
            id_ = FieldIndex.FieldIndex('id')
            catalog.addIndex('id', id_)

ZCATALOG_FIXTURE = ZCatalogLayer()


class TestZCatalog(unittest.TestCase):

    layer = ZCATALOG_FIXTURE

    def setUp(self):
        self.app = self.layer['app']
        self.catalog = self.app['catalog']

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

        # Add the folder to the ZODB
        self.app._setObject('foo_folder', foo_folder)
        foo_folder = self.app['foo_folder']
        bar_item = foo_folder['bar_item']

        # Register one item for an intid before catalogging but not
        # the other
        intids = component.getUtility(intid.IIntIds, context=self.app)
        bar_id = intids.register(bar_item)
        self.assertEqual(intids.queryId(foo_folder), None)

        # Catalog both items
        self.catalog.catalog_object(foo_folder)
        self.catalog.catalog_object(bar_item)

        # Once catalogged, the items have intid's, if already
        # registered the existing intid i
        foo_id = intids.getId(foo_folder)
        self.assertEqual(intids.getId(bar_item), bar_id)

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
        self.assertEqual(intids.getId(foo_folder), foo_id)
        self.assertEqual(intids.getId(bar_item), bar_id)

        # Query the catalog from a new ZODB connection
        # and check everything is working
        with z2.zopeApp() as app:
            self.assertTrue(app._p_jar is not self.app._p_jar)
            catalog = app['catalog']
            foo_brains = catalog(id=foo_folder.id)
            self.assertEqual(len(foo_brains), 1)
            bar_brains = catalog(id=bar_item.id)
            self.assertEqual(len(bar_brains), 1)
            self.assertEqual(foo_brains[0].getObject()._p_oid,
                             foo_folder._p_oid)
            self.assertEqual(bar_brains[0].getObject()._p_oid,
                             bar_item._p_oid)

            new_intids = component.getUtility(intid.IIntIds, context=app)
            self.assertEqual(new_intids.getId(foo_folder), foo_id)
            self.assertEqual(new_intids.getId(bar_item), bar_id)

        # When an item is renamed, it's intid and those of all
        # contained in the item are preserved
        newSecurityManager(None, SpecialUsers.system)
        self.app.manage_renameObjects(['foo_folder'], ['qux_folder'])
        z2.logout()
        foo_folder = self.app['qux_folder']
        bar_item = foo_folder['bar_item']
        self.assertEqual(intids.getId(foo_folder), foo_id)
        self.assertEqual(intids.getId(bar_item), bar_id)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestZCatalog))
    return suite
