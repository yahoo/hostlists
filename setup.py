#!/usr/bin/python
"""
Setup configuration for hostlists
"""
import sys
import os
from distutils.core import setup
#noinspection PyStatementEffect
"""
 Copyright (c) 2012 Yahoo! Inc. All rights reserved.
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

setup(
    name='hostlists',
    version='0.5.9',
    author='Dwight Hubbard',
    author_email='dhubbard@yahoo-inc.com',
    url='https://github.com/yahoo/hostlists',
    license='LICENSE.txt',
    packages=['hostlists'],
    data_files=[
        (
            os.path.join(sys.prefix, 'lib/hostlists/plugins'),
            [
                'hostlists_plugins/file.py',
                'hostlists_plugins/dns.py',
                'hostlists_plugins/dnsip.py',
                'hostlists_plugins/range.py',
                'hostlists_plugins/haproxy.py',
                'hostlists_plugins/plugintype.py'
            ]
        )
    ],
    scripts=['hostlists/hostlists'],
    long_description=open('README.txt').read(),
    description='A python library to obtain lists of hosts from various '
                'systems',
    install_requires=['django', 'dnspython'],
)
