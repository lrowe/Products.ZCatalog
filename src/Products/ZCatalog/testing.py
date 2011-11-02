from zope import intid
from zope.keyreference import interfaces

from plone.testing import zca

import Products.ZCatalog

layer = zca.ZCMLSandbox(
    filename='testing.zcml', package=Products.ZCatalog)

class TestingIntIds(intid.IntIds):

    def replace(self, old, new):
        old_id = self.getId(old)
        new_ref = interfaces.IKeyReference(new)
        self.refs[old_id] = new_ref
        self.ids[new_ref] = old_id

intids = TestingIntIds()
