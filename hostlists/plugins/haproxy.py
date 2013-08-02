#!/usr/bin/env python
""" haproxy host plugin """

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

#noinspection PyStatementEffect
"""
NOTE:
This script is primarily intended as a proof of concept of adding a load
balancer as the host IP address source.

THEORY OF OPERATION:
Since haproxy does not provide an externally accessible means of accessing
the backend names and states for hosts it is proxying this module uses ssh
to call a helper script on the haproxy server to get the information.

USAGE:
This plugin requires a signifcant amount of pre-configuration on the haproxy
server in order to work.  This requires a configuration change to enable
the stats socket in haproxy, setting permissions, and copying the get_haproxy_phys
script into place.

The setup steps are:

1. Enable the haproxy status socket, the script expects it to be /tmp/haproxy
   by adding:
        stats socket    /tmp/haproxy
   to the global section of the /etc/haproxy/haproxy.cfg file

2. Restart haproxy to create the socket

3. Make sure the socket file is owned by the user that will be connecting
   to the haproxy server.

4. Copy the get_haproxy_phys from the sshmap hostlists_plugins directory
   into the root of the home directory of the user that will be connecing
   to the haproxy server.
5. Set up the user's ~/.ssh/authorized_keys file to allow access via ssh
   without password.           
"""
import os
import urllib2
import base64
import json
import hostlists

def name():
  """ Name of plugins this plugin responds to """
  return ['haproxy','haproxy_all','haproxy_up','haproxy_down']

def plugin_type():
  """ Type of plugin this is """
  return ['vip']
  
def server_setting(server='default',setting=None):
  if not setting:
    return None
  settings=hostlists.get_setting('haproxy_plugin')
  if not settings:
    return None
  if server in settings.keys():
    if setting in settings[server].keys():
      return settings[server][setting]
  return None

# noinspection PyBroadException
def expand(value,name='haproxy',method=None):
  state='ALL'
  if name in ['haproxy_up']:
    state='UP'
  if name in ['haproxy_down']:
    state='DOWN'
  temp=value.split(':')
  if len(temp):
    haproxy=temp[0]
    if len(temp) > 1:
      backend=temp[1]
    else:
      backend='all'  
  else:
    return []
  # Determine settings
  # the last setting that is found is the setting so we go
  # from most generic to least
  # first some reasonable hardwired defaults
  timeout=2
  userid=None
  password=None
  # Next try and get setting defaults from the config file
  if server_setting('default','userid'):
    userid=server_setting('default','userid')
  if server_setting('default','password'):
    password=server_setting('default','password')
  if server_setting('default','timeout'):
    timeout=server_setting('default','timeout')
  if haproxy and not method and server_setting(haproxy,'method'):
    method=server_setting(haproxy,'method')
  if not method and server_setting('default','method'):
    method=server_setting('default','method')
  # Finally try settings specific to the server
  if haproxy:  
    if server_setting(haproxy,'userid'):
      userid=server_setting(haproxy,'userid')
    if server_setting(haproxy,'password'):
      password=server_setting(haproxy,'password')
    if server_setting(haproxy,'timeout'):
      timeout=server_setting(haproxy,'timeout')  
  tmplist=[]
  if method == 'ssh':
    command='ssh "%s" ./get_haproxy_phys "%s" "%s"'% (haproxy,backend,state)
    try:
      hosts=json.loads(os.popen(command).read())
      return hosts
    except:
      return []
  else:
    url="http://%s/haproxy?stats;csv" % haproxy
    request = urllib2.Request(url)
    if userid and password:
      base64string = base64.encodestring('%s:%s' % (userid, password)).replace('\n', '')
      request.add_header("Authorization", "Basic %s" % base64string)   
    try:
      result = urllib2.urlopen(request,timeout=timeout).read()
      for line in result.split('\n'):
        if not line.startswith('#') and len(line.strip()) and ',' in line:
          splitline=line.strip().split(',')
          if (splitline[0]==backend or backend.lower()=='all') and splitline[1] not in ['BACKEND','FRONTEND']:
            if state.upper() == 'ALL' or (splitline[17]==state):
              tmplist.append(splitline[1])
      return tmplist
    except urllib2.URLError:
      return []
