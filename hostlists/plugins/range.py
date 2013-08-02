#!/usr/bin/env python
""" hostlists plugin to get hosts from a file """

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


def name():
    """
    Plugin name
    """
    return 'range'


def expand(value):
    """
    Use Plugin to expand the value
    """
    return expand_item(value)


def block_to_list(block):
  """ Convert a range block into a numeric list 
      input "1-3,17,19-20"
      output=[1,2,3,17,19,20]
  """
  block+=','
  result=[]
  val=''
  in_range=False
  for letter in block:
    if letter in [',','-']:
      if in_range:
        val2=val
        val2_len=len(val2)
        #result+=range(int(val1),int(val2)+1)
        for value in range(int(val1),int(val2)+1):
          if val1.startswith('0'):
            result.append(str(value).zfill(val2_len))
          else:
            result.append(str(value))
        val=''
        val1=None
        in_range=False
      else:
        val1=val
        val1_len=len(val1)
        val=''
      if letter == ',':
        if val1 != None:
          result.append(val1.zfill(val1_len))
      else:
        in_range=True
    else:
      val+=letter
  return result


def expand_item(item):
  result=[]
  in_block=False
  pre_block=''
  for count in range(0,len(item)):
    letter=item[count]
    if letter == '[': 
      in_block=True
      block=''
    elif letter == ']' and in_block:
      in_block=False
      for value in block_to_list(block):
        result.append('%s%s%s'% (pre_block,value,item[count+1:]))
    elif in_block:
      block+=letter
    elif not in_block:
      pre_block += letter
  if len(result):
    return result
  else:
    return [item]
