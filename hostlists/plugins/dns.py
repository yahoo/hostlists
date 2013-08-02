#!/usr/bin/env python
""" hostlists plugin to get hosts from dns """

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


# noinspection PyUnresolvedReferences
import dns.resolver
import dns.reversename
def name():
  return 'dns'

# noinspection PyUnresolvedReferences
def expand(value):
  tmplist=[]
  addresses=[]
  try:
    answers = list(dns.resolver.query(value))
  except dns.resolver.NoAnswer:
    answers=[]
  for rdata in answers:
    addresses.append(rdata.address)
  for address in addresses:
    result=dns.reversename.from_address(address)
    try:
      # See if we can reverse resolv the IP address and insert
      # it only if it's a unique hostname.
      revaddress=str(dns.resolver.query(result,'PTR')[0]).strip('.')
      if revaddress not in tmplist:
        tmplist.append('type_vip:'+revaddress)
    except dns.resolver.NXDOMAIN:
      tmplist.append('type_vip:'+address)
  # if the tmplist with the reverse resolved hostnames
  # is not the same length as the list of addresses then
  # the site has the same hostname assigned to more than 
  # one IP address dns reverse resolving
  # If this happens we return the IP addresses because
  # they are unique, otherwise we return the hostnames.
  if len(tmplist) < len(addresses):
    return addresses
  return tmplist
  