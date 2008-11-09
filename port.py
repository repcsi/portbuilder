#!/usr/bin/env python
"""
Controller for various ports operations
"""
from logging import getLogger, FileHandler, DEBUG, INFO
from pypkg import run_main

handler = FileHandler('/tmp/pypkg/log', 'w')
handler.setLevel(DEBUG)
log = getLogger('pypkg')
log.addHandler(handler)
log.setLevel(INFO)

getLogger('pypkg.AutoExit').setLevel(DEBUG)

# TODO: Add pylint check for `R0401'

def main():
  """
     The main event loop.  This sets the program on the corrent trajectory and
     then exits.  Everything else just 'runs'
  """
  from pypkg.exit import terminate
  from pypkg.port import Port, get
  from pypkg import monitor
  from pypkg import target

  parser = gen_parser()
  options, args = parser.parse_args()
  options.args = args

  set_options(options)

  # Set the monitor
  if not options.no_opt:
    if options.stat_mode:
      if options.stat_mode < 0:
        parser.error("SEC needs to be positive, not %i" % options.stat_mode)
      monitor.set_monitor(monitor.Stat(options.stat_mode))
    else:
      monitor.set_monitor(monitor.Top())
  else:
    monitor.set_monitor(monitor.NoneMonitor())

  # Execute the primary build target
  if options.index:
    target.index_builder()
  else:
    callback = target.Caller(len(args), terminate)
    for i in args:
      port = get(i)
      if port:
        status = port.install_status()
        if (options.install and status == Port.ABSENT) or \
          (not options.install and status < Port.CURRENT):
          target.install_builder.put(port, callback)
        else:
          callback()
      else:
        callback()

  return

def gen_parser():
  """
     Create the options parser object

     @return: The options parser
     @rtype: C{OptionParser}
  """
  from optparse import OptionParser

  usage = "\t%prog [-bifnpu] [-w SEC] [-D variable] [variable=value] target ..."
  
  parser = OptionParser(usage, version="%prog 0.0.4")
  parser.add_option("-b", "--batch", action="store_true", default=False,
                    help="Batch mode.  Skips the config stage.")
  parser.add_option("-D", dest="make_env", action="append", metavar="variable",
                    default=[], help="Define the given variable for make (i.e."\
                    " add ``-D variable'' to the make calls.")
  parser.add_option("-i", "--install", action="store_true", default=True,
                    help="Install mode.  Installs the listed ports (and any " \
                    "dependancies required [default].")
  parser.add_option("-f", dest="fetch", action="store_true", default=False,
                    help="Only fetch the distribution files for the ports")
  parser.add_option("-n", dest="no_opt", action="store_true", default=False,
                    help="Display the commands that would have been executed, "\
                    "but do not actually execute them.")
  parser.add_option("-p", "--package", action="store_true", default=False,
                    help="When installing ports, also generate packages (i.e." \
                    " do a ``make package''.")
  parser.add_option("-u", "--update", dest="install", action="store_false",
                    default=True, help="Update mode.  Updates the given port." \
                    "  The last -i or -u will be the determining one.")
  parser.add_option("-w", dest="stat_mode", type="int", default=0, metavar="SEC"
                    , help="Use the stats monitor with SEC delay between lines")
  parser.add_option("--index", action="store_true", default=False,
                    help="Create the INDEX file for the ports infrastructure.")
  return parser

def set_options(options):
  """
     Set all the global options.

     @param options: The options
     @type options: C{object}
  """
  from pypkg.port import Port
  from pypkg import make

  # Add all -D options
  for i in options.make_env:
    make.env[i] = None

  # Add other make env options (aka variable=value)
  for i in options.args[:]:
    if i.find('=') != -1:
      # TODO:  Make sure var, val take the correct values
      var, val = i.split('=', 1)
      make.env[var] = val
      options.args.remove(i)

  # Batch mode, no configuring (-b)
  Port.force_noconfig = options.batch

  # Only fetch the ports
  Port.fetch_only = options.fetch

  # No operations (-n)
  if options.no_opt:
    make.no_opt = True

  # Package the ports after installing (-p)
  Port.package = options.package

run_main(main)
