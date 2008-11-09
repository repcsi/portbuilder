"""
The Cache module.  This module stores various items of information statically.
"""
from __future__ import absolute_import

from pypkg.cache.cachedb import CacheDB

__all__ = ['db']

db = CacheDB()  #: The databases used for caching

def check_files(db_name, name):
  """
     Check that the a set of files have not changed since the timestamp was
     taken.

     @param db_name: The database containing the timestamps
     @type db_name: C{str}
     @param name: The name that references the set of files
     @type name: C{str}
     @return: If the files have not changed
     @rtype: C{bool}
  """
  from cPickle import loads
  from os.path import exists, getmtime, getsize

  from pypkg.env import names

  files = db[names.get(db_name, db_name)].get(name)

  if not files:
    return False

  # TODO: handle corrupt data
  for path, stats in loads(files):
    if exists(path):
      if not stats or stats != (getmtime(path), getsize(path)):
        return False
    elif stats:
      return False

  return True

def set_files(db_name, name, files):
  """
     Sets the timestamps for a given set of files.

     @param db_name: The database containing the timestamps
     @type db_name: C{str}
     @param name: The name that references the set of files
     @type name: C{str}
     @param files: The set of files
     @type files: C{[str]}
  """
  from cPickle import dumps
  from os.path import exists, getmtime, getsize

  from pypkg.env import names

  data = []
  for i in files:
    if exists(i):
      data.append((i, (getmtime(i), getsize(i))))
    else:
      data.append((i, None))

  db[names.get(db_name, db_name)].put(name, dumps(data))
