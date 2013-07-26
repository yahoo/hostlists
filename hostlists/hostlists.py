#!/usr/bin/env python
""" 
A plugin extendable hostlist infrastructure 

This module provides functions for getting a list of hosts
from various systems as well as compressing the list into
a simplified list.

This module uses the hostlists_plugins python scripts
to actually obtain the listings.  
"""

#noinspection PyStatementEffect
"""
 Copyright (c) 2010 Yahoo! Inc. All rights reserved.
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

# Built in module imports
import os
import sys
import imp
import json
import logging
import re

# Global plugin cache so we don't constantly reload the plugin modules
global_plugins = { }

# A list of operators we use for set options
SET_OPERATORS = ['-']

# Config file
CONF_FILE = os.path.expanduser('~/.hostlists.conf')


# noinspection PyBroadException
def _get_plugins():
    """ Find all the hostlists plugins """
    plugins = global_plugins
    pluginlist = []
    plugin_path = [
        '~/.hostlists', '~/lib/hostlists', '/usr/lib/hostlists',
        '/home/y/lib/hostlists'
    ] + sys.path
    for directory in plugin_path:
        if os.path.isdir(os.path.join(directory, 'plugins')):
            templist = os.listdir(os.path.join(directory, 'plugins'))
            for item in templist:
                pluginlist.append(
                    os.path.join(os.path.join(directory, 'plugins'), item))
    pluginlist.sort()
    # Create a dict mapping the plugin name to the plugin method
    for item in pluginlist:
        if item.endswith('.py'):
            try:
                mod = imp.load_module(
                    'hostlists_plugins_%s' % os.path.basename(item[:-3]),
                    open(item),
                    item,
                    ('.py', 'r', imp.PY_SOURCE)
                )
                names = mod.name()
                if isinstance(names,(str,unicode)):
                    names = [names]
                for name in names:
                    if name not in plugins.keys():
                        plugins[name.lower()] = mod
            except:
                # Error in module import, probably a plugin bug
                logging.debug(
                    "Plugin import failed %s: %s" % (item,sys.exc_info()))
    return plugins


def get_setting(key):
    try:
        settings = json.load(open(CONF_FILE, 'r'))
    except IOError:
        # Couldn't open the settings file
        #print 'No such conf file'
        return None
    if key in settings.keys():
        return settings[key]
    return None


def expand(range_list, onepass = False):
    """
    Expand a list of lists and set operators into a final host lists 
    >>> hostlists.expand(['foo[01-10]','-','foo[04-06]'])
    ['foo09', 'foo08', 'foo07', 'foo02', 'foo01', 'foo03', 'foo10']
    >>> 
    """
    if isinstance(range_list,(str,unicode)):
        range_list = [range_list]
    new_list = []
    set1 = None
    operation = None
    for item in range_list:
        if set1 and operation:
            set2 = expand_item(item)
            new_list.append(list(set(set1).difference(set(set2))))
            set1 = None
            operation = None
        elif item in SET_OPERATORS and len(new_list):
            set1 = new_list.pop()
            operation = item
        else:
            expanded_item = expand_item(item, onepass = onepass)
            new_list.append(expanded_item)
    new_list2 = []
    for item in new_list:
        new_list2 += item
    return new_list2


def multiple_names(plugin):
    plugins = _get_plugins()
    count = 0
    for item in plugins.keys():
        if plugins[item] == plugin:
            count += 1
    if count > 1:
        return True
    else:
        return False


def expand_item(range_list, onepass = False):
    """ Expand a list of plugin:parameters into a list of hosts """
    #range_list=list(range_list)      
    # Find all the host list plugins
    if isinstance(range_list,(str,unicode)):
        range_list = [range_list]
    plugins = _get_plugins()

    # Iterate through our list
    newlist = []
    found_plugin = False
    for item in range_list:
        # Is the item a plugin
        temp = item.split(':')
        if len(temp) > 1:
            plugin = temp[0].lower()
            # Do we have a plugin that matches the passed plugin
            if plugin in plugins.keys():
                # Call the plugin
                item = None
                if multiple_names(plugins[plugin]):
                    newlist += plugins[plugin].expand(
                        ':'.join(temp[1:]).strip(':'), name = plugin)
                else:
                    newlist += plugins[plugin].expand(
                        ':'.join(temp[1:]).strip(':'))
                found_plugin = True
            else:
                print >> sys.stderr, 'plugin', plugin, 'not found', plugins.keys()
        else:
            # Default to running through the range plugin
            item = None
            newlist += plugins['range'].expand(temp[0])
        if item:
            newlist.append(item)
        # Recurse back through ourselves incase a plugin returns a value that
        # needs to be parsed
    # by another plugin.  For example a dns resource that has an address that
    # points to a load balancer vip that may container a number of hosts that
    # need to be looked up via the load_balancer plugin.
    if found_plugin and not onepass:
        newlist = expand_item(newlist)
    return newlist


def multikeysort(items, columns):
    from operator import itemgetter

    comparers = [
        (
            (itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)
        ) for col in columns
    ]

    def comparer(left, right):
        for fn, mult in comparers:
            try:
                result = cmp(fn(left), fn(right))
            except KeyError:
                return 0
            if result:
                return mult * result
        else:
            return 0

    return sorted(items, cmp = comparer)


def compress(hostnames):
    """
    Compress a list of host into a more compact range representation
    """
    domain_dict={}
    result=[]
    for host in hostnames:
        if '.' in host:
            domain='.'.join(host.split('.')[1:])
        else:
            domain=''
        try:
            domain_dict[domain].append(host)
        except KeyError:
            domain_dict[domain]=[host]
    domains=domain_dict.keys()
    domains.sort()
    for domain in domains:
        hosts=compress_domain(domain_dict[domain])
        result+=hosts
    return result


def compress_domain(hostnames):
    """
    Compress a list of hosts in a domain into a more compact representation
    """
    hostnames.sort()
    prev_dict = { 'prefix': "", 'suffix': '', 'number': 0 }
    items = []
    items_block = []
    new_hosts = []
    for host in hostnames:
        #print re.match(r"([^0-9]+)(\d+)(.+).?",sys.argv[1]).groups()
        try:
            parsed_dict = re.match(
                r"(?P<prefix>[^0-9]+)(?P<number>\d+)(?P<suffix>.+).?",
                host
            ).groupdict()
            # To generate the range we need the entries sorted numerically
            # but to ensure we don't loose any leading 0s we don't want to
            # replace the number parameter that is a string with the leading
            # 0s.
            parsed_dict['number_int'] = int(parsed_dict['number'])
            new_hosts.append(parsed_dict)
        except AttributeError:
            if '.' not in host:
                host += '.'
                parsed_dict = { 'host': compress([host])[0].strip('.') }
            else:
                parsed_dict = { 'host': host }
            new_hosts.append(parsed_dict)
    new_hosts = multikeysort(new_hosts, ['prefix', 'number_int'])
    for parsed_dict in new_hosts:
        if 'host' in parsed_dict.keys() or parsed_dict['prefix'] != prev_dict['prefix'] or parsed_dict['suffix'] != prev_dict['suffix'] or int(parsed_dict['number']) != int(prev_dict['number']) + 1:
            if len(items_block):
                items.append(items_block)
            items_block = [parsed_dict]
        else:
            items_block.append(parsed_dict)
        prev_dict = parsed_dict
    items.append(items_block)
    result = []
    for item in items:
        if len(item):
            if len(item) == 1 and 'host' in item[0].keys():
                result.append(item[0]['host'])
            elif len(item) == 1:
                result.append(
                    '%s%s%s' % (
                        item[0]['prefix'], item[0]['number'], item[0]['suffix']
                    )
                )
            else:
                result.append(
                    '%s[%s-%s]%s' % (
                        item[0]['prefix'], item[0]['number'], item[-1]['number'], item[0]['suffix']
                    )
                )
    return result


def range_split(hosts):
    """ Split up a range string, this needs to separate comma separated
    items unless they are within square brackets and split out set operations
    as separate items."""
    in_brackets = False
    current = ""
    result_list = []
    for c in hosts:
        if c in ['[']:
            in_brackets = True
        if c in [']']:
            in_brackets = False
        if not in_brackets and c == ',':
            result_list.append(current)
            current = ""
        elif not in_brackets and c == '-':
            result_list.append(current)
            result_list.append('-')
            current = ""
        elif not in_brackets and c in [','] and len(current) == 0:
            pass
        else:
            current += c
    if len(current):
        result_list.append(current)
    return result_list


if __name__ == "__main__":
    # This has been moved to the hostlist script
    pass
