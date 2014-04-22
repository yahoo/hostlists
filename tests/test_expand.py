#!/usr/bin/env python
#Copyright (c) 2012 Yahoo! Inc. All rights reserved.
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License. See accompanying LICENSE file.
"""
Unit tests of sshmap
"""
__author__ = 'dhubbard'
import hostlists
import unittest


class TestHostlistsExpand(unittest.TestCase):
    """
    hostmap unit tests
    """
    def set_up(self):
        pass

    class base_test_expand_string_input(unittest.TestCase):
        range_list = 'localhost'
        expected_result = ['localhost']

        def __init__(self):
            result = hostlists.expand(self.range_list)
            self.assertIsInstance(result, list)
            self.assertListEqual(result, self.expected_result)

    class test_expand__string_input__single_host(base_test_expand_string_input):
        """ Expand a string with a single host
        """
        range_list = 'localhost'
        expected_result = ['localhost']

    class test_expand__string_input__multiple_host(
        base_test_expand_string_input
    ):
        """
        Expand a string containing multiple comma seperated hosts
        """
        range_list = 'localhost, foobar'
        expected_result = ['localhost', 'foobar']

    class test_expand__string_input__multiple_host__range(
        base_test_expand_string_input
    ):
        range_list = 'localhost[3-5], foobar'
        expected_result = [
            'localhost3', 'localhost4', 'localhost5', 'foobar'
        ]

    class disabled_test_expand__string_input__multiple_host__range_gap(
        base_test_expand_string_input
    ):
        range_list = 'localhost[3-5,7], foobar'
        expected_result = [
            'localhost3', 'localhost4', 'localhost5', 'localhost7', 'foobar'
        ]


if __name__ == '__main__':
    unittest.main()
