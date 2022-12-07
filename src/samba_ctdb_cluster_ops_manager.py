"""SambaCTDBManager Class"""

import subprocess
import sys

#CTDB_PKGS = ['smbclient', 'samba', 'ctdb', 'winbind', 'libnss-winbind',
#        'libpam-winbind', 'krb5-user', 'quota', 'acl']
# krb5-user should probably be installed later by some sssd subordinate
CTDB_PKGS = ['smbclient', 'samba', 'ctdb', 'winbind', 'libnss-winbind',
        'libpam-winbind', 'quota', 'acl']

class SambaCTDBManager:
    """
    Mangages the CTDB service, such as installing, configuring, etc.
    This class should work independently from juju, such as that it can
    be tested without lauching a full juju environment.
    """

    def stop_ctdb(self):
        """Stop CTDB"""
        try:
            subprocess.run(['systemctl','stop','ctdb'], check = True)
        except Exception as e:
            print("Error stopping ctdb", str(e))

    def start_ctdb(self):
        """Start ctdb"""
        try:
            subprocess.run(['systemctl','start','ctdb'], check = True)            
        except Exception as e:
            print("Error starting ctdb", str(e))
    
    def restart_ctdb(self):
        """Restart ctdb"""
        try:
            subprocess.run(['systemctl','restart','ctdb'], check = True)            
        except Exception as e:
            print("Error starting ctdb", str(e))

    def install_ctdb(self):
        """
        Install packages. Juju has already run apt-get upgrade.
        Afterwards, services smbd, nmbd, winbind and ctdb are enabled,
        but ctdb is dead.
        """
        try:
            cmd = ['apt', 'install', '-y']
            cmd.extend(CTDB_PKGS)
            subprocess.run(cmd, check = True)
        except Exception as e:
            print("Error installing ctdb", str(e))
            sys.exit(1)

    def remove_ctdb(self):
        """
        Uninstall packages and traces of the charm.
        """
        try:
            cmd = ['apt', 'purge', '-y']
            cmd.extend(CTDB_PKGS)
            subprocess.run(cmd, check = True)
        except Exception as e:
            print("Error uninstalling ctdb", str(e))
            sys.exit(1)

    def ctdb_version(self):
        """ Return the version of ctdb as a string or None"""
        try:
            ver = subprocess.run(['ctdb','version'],
                    capture_output=True).stdout.decode()
            return ver
        except Exception as e:
            print("Error getting version from ctdb", e)
            return None
