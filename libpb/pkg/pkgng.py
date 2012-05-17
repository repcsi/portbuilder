"""
The next generation package management tools (i.e. pkgng)..
"""
from __future__ import absolute_import

import os

from libpb import env

__all__ = ["add", "info"]

shell_pkg_add = """
if [ ! -d %(wrkdir)s ]; then
    mkdir -p %(wrkdir)s;
    clean_wrkdir="YES";
fi;
tar -xf %(pkgfile)s -C %(wrkdir)s -s ",/.*/,,g" "*/pkg-static";
%(wrkdir)s/pkg-static add %(pkgfile)s;
rm -f %(wrkdir)s/pkg-static;
if [ "$clean_wrkdir" = "YES" ]; then
    rmdir %(wrkdir)s;
fi
"""

os.environ["ASSUME_ALWAYS_YES"] = "YES"

def add(port, repo=False, pkg_dir=None):
    """Add a package for port."""
    if port.attr["pkgname"].rsplit('-', 1)[0] == "pkg":
        # Special case when adding the `pkg' as it provides the functionality
        # and thus cannot add itself (or so one would thing).
        if repo or pkg_dir:
            # TODO: support installing pkg from a custom $PKGDIR
            args = False
        else:
            args = ("sh", "-c", shell_pkg_add % port.attr)
    else:
        # Normal package add
        if repo:
            args = ("install", "-y", port.attr["pkgname"])
        elif pkg_dir:
            args = ("add", os.path.join(pkg_dir, port.attr["pkgname"], ".txz"))
        else:
            args = ("add", port.attr["pkgfile"])
    if args:
        if env.flags["chroot"]:
            args = ("pkg", "-c", env.flags["chroot"]) + args
        else:
            args = ("pkg",) + args
    return args


def info():
    """List all installed packages with their respective port origin."""
    if env.flags["chroot"]:
        args = ("pkg", "-c", env.flags["chroot"], "info", "-ao")
    else:
        args = ("pkg", "info", "-ao")
    return args
