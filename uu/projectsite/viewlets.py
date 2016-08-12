from plone.app.layout.viewlets.common import ViewletBase
from zope.component.hooks import getSite


class BaseJSRewriteViewlet(ViewletBase):
    
    def index(self, *args, **kwargs):
        siteurl = getSite().absolute_url()
        scripttag = '<script type="text/javascript" src="%s"></script>' % (
            '/'.join((siteurl, '++resource++fixbase.js'))
            )
        return scripttag

