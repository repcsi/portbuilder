"""
The architecture module.  This module contains the architecture specific code.
"""
from __future__ import absolute_import

__all__ = ['attr', 'status']

from pypkg.port.arch.freebsd_ports import get_attr, get_status as status

def attr(origin):
  """
     Retrieves the attributes for a given port, using the cached version when
     possible.

     @param origin: The port identifier
     @type origin: C{str}
     @return: A dictionary of attributes
     @rtype: C{\{str:str|(str)|\}}
  """
  from logging import getLogger
  
  from pypkg.cache import db, check_files, set_files

  files = check_files('port.makefiles', origin)

  if files:
    try:
      return db['port.attr'][origin]
    except KeyError:
      getLogger('pypkg.cache').warn('Corrupt data detected (port.attr.%s)' %
                                                                        origin)
  
  att = get_attr(origin)
  db['port.attr'][origin] = att
  set_files('port.makefiles', origin, att['makefiles'])
  return att
