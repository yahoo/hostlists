#!/usr/bin/python
"""
Setup configuration for hostlists
"""
__license__ = """
 Copyright (c) 2010-2013 Yahoo! Inc. All rights reserved.
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License. See accompanying LICENSE file.
"""
import os
import sys
from distutils.core import setup


setup(
    name='hostlists',
    version='0.5.16',
    author='Dwight Hubbard',
    author_email='dhubbard@yahoo-inc.com',
    url='https://github.com/yahoo/hostlists',
    license='LICENSE.txt',
    packages=['hostlists'],
    data_files=[
        (
            os.path.join(sys.prefix, 'lib/hostlists/plugins'),
            [
                'hostlists/plugins/dns.py',
                'hostlists/plugins/dnsip.py',
                'hostlists/plugins/file.py',
                'hostlists/plugins/haproxy.py',
                'hostlists/plugins/range.py',
                'hostlists/plugins/plugintype.py'
            ]
        )
    ],
    scripts=['hostlists/hostlists'],
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],
    description='A python library to obtain lists of hosts from various '
                'systems',
    install_requires=['django', 'dnspython'],
)
