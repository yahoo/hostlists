#!/usr/bin/env python
"""
hostlists plugin to recursively query plugins based on type.

This makes it possible to obtain lists of hosts by recursively
querying multiple backends.

For example:
   * Query dns for www.foo.com
   * Get a list of two hostnames back haproxy1.ny.foo.com and
     haproxy1.lax.foo.com.
   * Query reverse proxies and load balancers for the 
     above two hostnames and the names of any hosts serving 
     the traffic for them.  haproxy1.ny.foo.com is a vip being 
     served by apache1.ny.foo.com ad apache2.ny.foo.com. 
     haproxy1.lax.foo.com is a vip being serviced by
     apache2.lax.foo.com, apache3.lax.foo.com and
     joesdesktop.foo.com. 
   * Return apache[1-2].ny.foo.com, apache[2-3].lax.foo.com,
     joesdektop.foo.com 
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

import hostlists

def name():
  return ['type','type_vip','type_vip_up','type_vip_down']

def expand(value,name=None):
  """ Try all plugins of a specific type for a result, if none
  are able to expand the value further then return just the value """
  mod_type='vip'
  if not name:
    return [value]
  if name.lower() in ['type_vip']:
    mod_type='vip'
    filter_append=''
  if name.lower() in ['type_vip_down']:
    mod_type='vip_down'
    filter_append='_down'
  if name.lower() in ['type_vip_up']:
    mod_type='vip_up'
    filter_append='_up'
  plugins=hostlists._get_plugins()
  for plugin_name in plugins.keys():
    if ( 
      (filter_append != '' and plugin_name.endswith(filter_append)) or
      (filter_append == '' and plugin_name.find('_') == -1) 
    ):
      try:
        if mod_type in plugins[plugin_name].type():
          name=plugin_name+filter_append
          result=plugins[plugin_name].expand(value,name=name)
          if len(result):
            return result
      except AttributeError:
        pass
  return [value]
  
