"""
1. Install plone.app.widgets add on
2. Run following install steps for:
  uu.projectsite: jsregistry.xml
  uu.projectsite: registry.xml
  uu.projectsite: importsteps.xml
"""

import transaction
from zope.component.hooks import setSite

try:
    from clearwind.arecibo.interfaces import IAreciboConfiguration
    HAS_ARECIBO = True
except ImportError:
    HAS_ARECIBO = False


_installed = lambda site: site.portal_quickinstaller.isProductInstalled
product_installed = lambda site, name: _installed(site)(name)

PKGNAME = 'clearwind.arecibo'
BASEPATH = '/VirtualHostBase/https/teamspace1.upiq.org'


def commit(context, msg):
    txn = transaction.get()
    # Undo path, if you want to use it, unfortunately is site-specific,
    # so use the hostname used to access all Plone sites.
    txn.note('%s%s' % (BASEPATH, '/'.join(context.getPhysicalPath())))
    txn.note(msg)
    txn.commit()


def uninstall_utility(site):
    name = 'Arecibo_config'
    sm = site.getSiteManager()
    util = sm.queryUtility(IAreciboConfiguration, name=name)
    sm.unregisterUtility(util, IAreciboConfiguration, name=name)
    sm.utilities.unsubscribe((), IAreciboConfiguration)
    assert IAreciboConfiguration not in sm.utilities._provided
    assert IAreciboConfiguration not in sm.utilities._subscribers[0]
    del util
    sm._p_changed = True


def uninstall_product(site):
    _id = lambda d: d.get('id')
    qi = site.portal_quickinstaller
    if PKGNAME in map(_id, qi.listInstalledProducts()):
        qi.uninstallProducts([PKGNAME])


def update(site):
    uninstall_utility(site)
    uninstall_product(site)
    commit(site, 'Removed arecibo for site %s' % site.getId())


def main(app):
    for site in app.objectValues('Plone Site'):
        if not product_installed(site, PKGNAME):
            continue
        setSite(site)
        update(site)


if __name__ == '__main__' and 'app' in locals():
    main(app)  # noqa

