from setuptools import setup, find_packages

version = '0.1'

setup(
    name='uu.projectsite',
    version=version,
    description="Policy product for UPIQ Teamspace and Plone 4.x sites",
    long_description=(
        open("README.rst").read() + "\n" +
        open("CHANGES.rst").read()
        ),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
    keywords='',
    author='Sean Upton',
    author_email='sean.upton@hsc.utah.edu',
    url='https://github.com/upiq',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['uu'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'collective.teamwork',
        'uu.formlibrary',
        'uu.chart',
        'uu.staticmap',
        'uu.eventintegration',
        'Products.CMFPlone',
        'plone.browserlayer',
        'z3c.jbot',
        'five.pt',
        'wildcard.media',
        'collective.cover',
        'collective.inviting',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
