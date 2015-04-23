# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Invenio is a framework for digital libraries and data repositories.

Invenio enables you to run your own digital library or document
repository on the web.  Invenio covers all aspects of digital library
management, from document ingestion, through classification, indexing
and further processing, to curation, archiving, and dissemination.
The flexibility and performance of Invenio make it a comprehensive
solution for management of document repositories of moderate to large
sizes (several millions of records).

Links
-----

* `website <http://invenio-software.org/>`_
* `documentation <http://invenio.readthedocs.org/en/latest/>`_
* `development <https://github.com/inveniosoftware/invenio>`_

"""

from setuptools import setup

setup(
    name='invenio-obelix',
    version=0.1,
    description='Invenio integration with Obelix recommendation system.',
    url='https://github.com/inveniosoftware/invenio-obelix',
    license='GPLv2',
    author='CERN',
    author_email='info@invenio-software.org',
    long_description=__doc__,
    packages=['invenio_obelix'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        #'click>=2.0',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

