from zope.component import queryUtility

from collective.teamwork.user.config import add_workgroup_type
from collective.teamwork.user.interfaces import IWorkgroupTypes


# additional integration-specific roles to integrate with collective.teamwork
CONFIG = {
    'forms': {
        'groupid': u'forms',
        'title': u'Form entry',
        'description': u'Form entry and submission for workspace context.',
        'roles': [u'FormEntry'],
    }
}

ROLE_KEYS = ('viewers', 'forms', 'contributors', 'managers')


def register():
    add_workgroup_type('forms', CONFIG.get('forms'))
    config = queryUtility(IWorkgroupTypes)
    config.order = ROLE_KEYS

