#!/usr/bin/env python
""" hostlists plugin to get hosts from a file """


def name():
  return ['file']

# noinspection PyUnusedLocal
def expand(value,name="file"):
  tmplist=[]
  for host in [i.strip() for i in open(value,'r').readlines()]:
    if not host.startswith('#') and len(host.strip()):
      tmplist.append(host)
  return tmplist
  