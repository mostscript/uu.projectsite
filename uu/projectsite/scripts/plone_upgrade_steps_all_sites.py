from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.MigrationTool import ADDON_LIST
from Products.CMFPlone.utils import getFSVersionTuple
import transaction
from zope.component.hooks import setSite


PLONE4 = getFSVersionTuple()[0] == 4


def fix_js_registry(site):
    """
    fix Plone 4 JS registry, which may be broken by upgrading one or more
    of the above profiles (jQueryTools scripts get disabled by default)
    """
    jsreg = site.portal_javascripts
    js_ids = (
        '++resource++plone.app.jquerytools.dateinput.js',
        '++resource++plone.app.jquerytools.validator.js',
        )
    for resource_id in js_ids:
        jsreg.getResource(resource_id).setEnabled(True)
    jsreg.cookResources()


def upgrade_applicable(site, profiles):
    """Given profile ids, upgrade only if upgrades available"""
    gs = site.portal_setup
    # upgrade profile(s)
    for profile in profiles:
        if gs.listUpgrades(profile):
            # we only upgrade when upgrade exists, more subtle than
            # portal_migration implementation, but to same effect.
            gs.upgradeProfile(profile)


def upgrade(site, profiles=(_DEFAULT_PROFILE,)):
    print ' == %s == ' % site.getId()
    profiles = list(profiles)
    # extend with "core" plone add-ons:
    profiles.extend([str(o.profile_id) for o in ADDON_LIST])
    upgrade_applicable(site, profiles)
    if PLONE4:
        fix_js_registry(site)
    txn = transaction.get()
    txn.note(
        'Upgrade Plone profile, fix JS registry for site %s' % site.getId()
        )
    txn.commit()


def main(app):
    for site in app.objectValues('Plone Site'):
        setSite(site)
        upgrade(site)


if __name__ == '__main__' and 'app' in locals():
    main(app)  # noqa
