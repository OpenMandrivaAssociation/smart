if not sysconf.getReadOnly():
    if not sysconf.has("channels"):
	sysconf.set("rpm-check-signatures", False)

    sysconf.set("force-channelsync", True);

    if not sysconf.has("install-suggests"):
	sysconf.set("install-suggests", False);

    if not sysconf.has("package-tree"):
	sysconf.set("package-tree", "none");

    if not sysconf.has("package-columns"):
	sysconf.set("package-columns", "name,version,size,description");

    if not sysconf.has("pycurl"):
	sysconf.set("pycurl", True);

    if not sysconf.has("prefer-origin"):
	sysconf.set("prefer-origin", True);

    if not sysconf.has("socket-timeout"):
	sysconf.set("socket-timeout", 10);


from smart.channel import *
from smart.commands.mirror import *
from smart import *
import os

MIRRORSDIR = "/etc/smart/mirrors/"

def syncMirrors(mirrorsdir, force=None):

    if os.path.isdir(mirrorsdir):

        sysconf.remove("mirrors")

	for entry in os.listdir(mirrorsdir):
            if not (entry.endswith(".mirror") or entry.endswith(".mirrors")):
                continue

            filepath = os.path.join(mirrorsdir, entry)
            if not os.path.isfile(filepath):
                continue

            try:
                data = read_mirrors(ctrl, filepath)
                for i in range(0,len(data),2):
                    origin, mirror = data[i:i+2]
                    if mirror:
                        sysconf.add(("mirrors", origin), mirror, unique=True)
                        iface.debug("distro.py syncMirrors: Adding mirror %s to origin %s" % (mirror, origin))
            except Error, e:
                iface.error(_("While using %s: %s") % (filepath, e))
                continue


if not sysconf.getReadOnly():
    syncMirrors(sysconf.get("mirror-sync-dir", MIRRORSDIR))

