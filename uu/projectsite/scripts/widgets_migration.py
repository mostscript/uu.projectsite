
"""
1. Install plone.app.widgets add on
2. Run following install steps for:
  uu.projectsite: jsregistry.xml
  uu.projectsite: registry.xml
  uu.projectsite: importsteps.xml
"""

from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.MigrationTool import ADDON_LIST
import transaction
from zope.component.hooks import setSite


_installed = lambda site: site.portal_quickinstaller.isProductInstalled
product_installed = lambda site, name: _installed(site)(name)

PKGNAME = 'uu.projectsite'
BASEPATH = '/VirtualHostBase/https/teamspace1.upiq.org'


def commit(context, msg):
    txn = transaction.get()
    # Undo path, if you want to use it, unfortunately is site-specific,
    # so use the hostname used to access all Plone sites.
    txn.note('%s%s' % (BASEPATH, '/'.join(context.getPhysicalPath())))
    txn.note(msg)
    txn.commit()


def install_plone_app_widgets(site):
    sitename = site.getId()
    pid = 'plone.app.widgets'
    _id= lambda d: d.get('id')
    qi = site.portal_quickinstaller
    if pid not in map(_id, qi.listInstallableProducts()):
        if pid not in (map(_id, qi.listInstalledProducts())):
            raise RuntimeError('%s not installable product (%s).' % (
                pid,
                sitename
                ))
        else:
            print 'INFO: %s already installed for site %s' % (pid, sitename)
    qi.installProduct(pid)
    print 'INFO: plone.app.widgets installed (%s)' % (sitename,)


def update_product_steps(site, profile, steps):
    gs = site.portal_setup
    for step_id in steps:
        gs.runImportStepFromProfile(profile, step_id)
        print 'INFO: installed step (%s): %s' % (profile, step_id)

def update_projectsite_steps(site):
    profile =  u'uu.projectsite:default'
    steps = [
        u'plone.app.registry',
        u'jsregistry',
        u'uu.projectsite-widgetsjsorder'
        ]
    update_product_steps(site, profile, steps)


def update_formlibrary_steps(site):
    profile =  u'uu.formlibrary:default'
    steps = [
        u'jsregistry',
        ]
    update_product_steps(site, profile, steps)


def upgrade(site):
    install_plone_app_widgets(site)
    update_projectsite_steps(site)
    update_formlibrary_steps(site)
    commit(site, 'Installed widget updates for site %s' % site.getId())


def main(app):
    for site in app.objectValues('Plone Site'):
        if not product_installed(site, PKGNAME):
            continue
        setSite(site)
        upgrade(site)


if __name__ == '__main__' and 'app' in locals():
    main(app)  # noqa
