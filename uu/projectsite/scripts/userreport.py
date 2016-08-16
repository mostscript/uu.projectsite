"""
Run script for:

Usage report for UPIQ hosted QI teamspace sites, including partner sites,
excluding non-billable (UPIQ staff, testing) users.
"""

import csv
import os
import re
from datetime import date, timedelta

from zope.component.hooks import setSite
from zope.interface import Interface, implements
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName

from collective.teamwork.interfaces import IProjectContext
from collective.teamwork.interfaces import WORKSPACE_TYPES
from collective.teamwork.user.interfaces import IWorkspaceRoster


_u = lambda v: v.decode('utf-8') if isinstance(v, str) else unicode(v)
_utf8 = lambda v: v.encode('utf-8') if isinstance(v, unicode) else v


_mkvocab = lambda seq: SimpleVocabulary([SimpleTerm(t) for t in seq])


_installed = lambda site: site.portal_quickinstaller.isProductInstalled
product_installed = lambda site, name: _installed(site)(name)


DETAIL_DEBUG = False

PKGNAME = 'uu.projectsite'


# ignored users are typically site-testing users of project managers
# who have other primary userid/email identification we care about
# reporting on without duplication.  Match on substring of email address:
USER_IGNORE = (
    # UPIQ:
    'sdupton',
    'snaeole',
    'homa.rehmani',
    # OPIP:
    'ross8305',
    'davidrossmph',
    'ktconner3',
    # CNHNQI:
    'tamaranjohn',
    # MAINE:
    'mainetesting@teamspace.mainequalitycounts.org',
    # TNAAP:
    'becky810',
    'darcy.knowles'
    )


upiq_user = lambda u: 'hsc.utah.edu' in str(u) or 'upiq.org' in str(u)
_ignore_user = lambda u: any(map(lambda substr: substr in u, USER_IGNORE))
ignore_user = lambda u: upiq_user(u) or _ignore_user(u.lower())


#DIRNAME = 'usage_data_folder'
DIRNAME = '/var/www/usage'


MONTHS = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}


class IProjectSnapshot(Interface):
    name = schema.BytesLine()
    title = schema.TextLine()
    month = schema.Choice(
        vocabulary=_mkvocab(MONTHS.values()),
        )
    date = schema.Date()
    all_users = schema.Set()
    managers = schema.Set()
    form_users = schema.Set()
    project_count = schema.Int(constraint=lambda v: v >= 0)
    team_count = schema.Int(constraint=lambda v: v >= 0)


class ProjectSnapshot(object):
    
    implements(IProjectSnapshot)
    
    NAMES = schema.getFieldNamesInOrder(IProjectSnapshot)
    
    def __init__(self, **kwargs):
        
        # initially empty sets for users, can be intersected later
        self.all_users = set()
        self.other_users = set()
        self.managers = set()
        self.form_users = set()
        for k, v in kwargs.items():
            if k in self.NAMES:
                IProjectSnapshot[k].validate(v)
                setattr(self, k, v)
    
    def __setattr__(self, name, value):
        """Validating setattr for any schema fields"""
        if name in self.NAMES:
            IProjectSnapshot[name].validate(value)
        self.__dict__[name] = value


def is_end_of_month(datestamp):
    next_day = datestamp + timedelta(days=1)
    if next_day.month != datestamp.month:
        return True
    return False


def all_workspaces(project):
    """
    Return flattened list of all contained workspaces,
    including project itself.
    """
    catalog = getToolByName(project, 'portal_catalog')
    r = catalog.unrestrictedSearchResults({
        'portal_type': WORKSPACE_TYPES,
        'path': {'query': '/'.join(project.getPhysicalPath())},
        })
    workspaces = map(lambda b: b._unrestrictedGetObject(), r)
    return workspaces


def form_users(workspace):
    """Given a workspace, get the ids of users with forms role"""
    roster = IWorkspaceRoster(workspace)
    _formusers = set(roster.groups['forms'].keys())
    _leads = set(roster.groups['managers'].keys())
    return list(_formusers | _leads)


def merged_form_users(project):
    """
    Given a project, get de-duped set of form users from all
    contained workspaces, not including managers at root of the
    project.
    """
    workspaces = all_workspaces(project)
    _form_users = [form_users(w) for w in workspaces]
    merged = set(reduce(lambda a, b: set(a) | set(b), _form_users))
    exclude = set(IWorkspaceRoster(project).groups['managers'].keys())
    return list(merged - exclude)


def other_users(project):
    """
    Given project, get de-duped list of users who are neither form
    users nor project managers.
    """
    form_users = set(merged_form_users(project))
    managers = set(IWorkspaceRoster(project).groups['managers'].keys())
    all_users = set(IWorkspaceRoster(project).keys())
    return ((all_users - managers) - form_users)


def filtered_users(c):
    """
    Given collection c of users, return list of non-ignored
    users.
    """
    return [u for u in c if not ignore_user(u)]


def output_value(k, v):
    """Given key and value k, v -- normalize output value for CSV"""
    if isinstance(v, set):
        v = len(v)  # output the count, not sequence/set
    return _utf8(v)


def report_main(site, datestamp, perproject=False):
    """
    Given site and datestamp for snapshot, append report result to
    file named project_users.csv with column format:
    
    month, date, project_name, #users, #managers, #teams, #forms.
    """
    if DETAIL_DEBUG:
        print '###### SITE REPORT DETAIL: %s ######' % site.getId()

    catalog = getToolByName(site, 'portal_catalog')
    r = catalog.unrestrictedSearchResults(
        {'object_provides': IProjectContext.__identifier__}
        )
    projects = [brain._unrestrictedGetObject() for brain in r]
    if not os.path.isdir(DIRNAME):
        os.mkdir(DIRNAME)
    columns = (
        'month',
        'date',
        'all_users',
        'managers',
        'form_users',
        'other_users',
        'project_count',
        'team_count',
        )
    sitesnap = ProjectSnapshot(
        name='site-%s' % site.getId(),
        title=_u(site.Title()),
        date=datestamp,
        month=MONTHS.get(datestamp.month),
        )
    sitesnap.project_count = 0
    sitesnap.team_count = 0
    site_filename = os.path.join(DIRNAME, '%s.csv' % sitesnap.name)
    if os.path.exists(site_filename):
        out = open(site_filename, 'r')
        data = out.readlines()
        out.close()
        if any([(str(datestamp) in line) for line in data]):
            return  # already have site report for date, done with this site
        site_out = open(site_filename, 'a')  # append to EOF
    else:
        site_out = open(site_filename, 'w')  # will create
        site_out.write('%s\n' % ','.join(columns))  # new file, ergo headings
    for project in projects:
        sitesnap.project_count += 1
        roster = IWorkspaceRoster(project)
        snapshot = ProjectSnapshot(
            name=project.getId(),
            title=_u(project.Title()),
            )
        snapshot.project_count = 1
        snapshot.date = datestamp
        snapshot.month = MONTHS.get(datestamp.month)
        snapshot.all_users = set(filtered_users(roster))
        sitesnap.all_users = sitesnap.all_users.union(snapshot.all_users)
        snapshot.other_users = set(filtered_users(other_users(project)))
        snapshot.managers = set(
            filtered_users(
                roster.groups['managers'].keys()
                )
            )
        sitesnap.managers = sitesnap.managers.union(snapshot.managers)
        snapshot.form_users = set(
            filtered_users(
                merged_form_users(project)
                )
            )
        sitesnap.form_users = sitesnap.form_users.union(snapshot.form_users)
        snapshot.team_count = len(all_workspaces(project)) - 1
        sitesnap.team_count += snapshot.team_count
        if DETAIL_DEBUG:
            print '== PROJECT: %s ==' % project.getId()
            print '  Team workspace count: %s' % snapshot.team_count 
            print '  Total users (all categories): %s' % len(snapshot.all_users)
            print '   Managers of project: %s' % len(snapshot.managers)
            for email in snapshot.managers:
                print '\t   - %s' % email
            print '   Form entry users, incl. team managers who are not project managers: %s' % len(snapshot.form_users)
            for email in snapshot.form_users:
                print '\t   - %s' % email
            print '   Other users (not managers, not form entry): %s' % len(snapshot.other_users)
            for email in snapshot.other_users:
                print '\t   - %s' % email
        
        if perproject:
            proj_filename = os.path.join(DIRNAME, '%s-%s.csv' % (
                site.getId(),
                project.getId(),
                ))
            if os.path.exists(proj_filename):
                out = open(proj_filename, 'r')
                data = out.readlines()  # existing data in file
                out.close()
                if any([(str(datestamp) in line) for line in data]):
                    continue  # don't duplicate entry for date already in file
                out = open(proj_filename, 'a')  # append to EOF
            else:
                out = open(proj_filename, 'w')  # will create
                out.write('%s\n' % ','.join(columns))  # new file -> headings
            writer = csv.DictWriter(out, columns, extrasaction='ignore')
            # write row to CSV from snapshot, convert u'' to utf-8 as needed
            writer.writerow(
                dict([(k, output_value(k, v))
                      for k, v in snapshot.__dict__.items()]))
            out.close()

    # now normalize site-wide users for greatest role... if a user is manager
    # in project A, do not include them in form users just because they have
    # form user role in project B:
    sitesnap.form_users = sitesnap.form_users - sitesnap.managers
    sitesnap.other_users = (sitesnap.all_users - sitesnap.managers) - (
        sitesnap.form_users)
    # final reconciliation, do not include any users in specific lists
    # if not in all_users group:
    sitesnap.form_users = sitesnap.form_users.intersection(sitesnap.all_users)
    sitesnap.managers = sitesnap.managers.intersection(sitesnap.all_users)
    
    if DETAIL_DEBUG:
        print '== SITE: %s ==' % site.getId()
        print '  Total UNIQUE users (all categories): %s' % len(sitesnap.all_users)
        print '   UNIQUE managers of project: %s' % len(sitesnap.managers)
        for email in sitesnap.managers:
            print '\t   - %s' % email
        print '   UNIQUE form entry users, incl. team managers who are not project managers: %s' % len(sitesnap.form_users)
        for email in sitesnap.form_users:
            print '\t   - %s' % email
        print '   UNIQUE other users (not managers, not form entry): %s' % len(sitesnap.other_users)
        for email in sitesnap.other_users:
            print '\t   - %s' % email

    site_writer = csv.DictWriter(site_out, columns, extrasaction='ignore')
    site_writer.writerow(
        dict([(k, output_value(k, v)) for k, v in sitesnap.__dict__.items()]))
    site_out.close()


def main(app, datestamp=None, username='admin'):
    for site in app.objectValues('Plone Site'):
        if not product_installed(site, PKGNAME):
            continue
        setSite(site)
        # user spoofins, try site user folder and instance/app/root user folder
        contexts = (site, app)
        for context in contexts:
            uf = context.acl_users
            user = uf.getUserById(username)
            if user is not None:
                newSecurityManager(None, user)
                break
        if user is None:
            raise RuntimeError('Unable to obtain user for username %s' % (
                username,))
        report_main(site, datestamp)


def normalized_date(value):
    value = str(value).strip()
    match = lambda v: re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$').search(v)
    if match(value):
        year, month, day = (value[0:4], value[5:7], value[8:10])
        return date(*[int(v) for v in (year, month, day)])
    return date.today()  # default


if 'app' in locals():
    import sys
    datestamp = date.today()
    if len(sys.argv) > 1:
        datestamp = normalized_date(sys.argv[-1])
    main(app, datestamp)  # noqa

