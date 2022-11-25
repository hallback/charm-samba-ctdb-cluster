"""SambaCTDBClusterOpsManager Class"""

import subprocess

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

    def install_ctdb(self, resource_file):
        """ Installs from a supplied zip file resource """
        # actually install packages

    def ctdb_version(self):
        """ Return the version of ctdb as a string or None"""
        try:
            ver = subprocess.run(['ctdb','version'],
                    capture_output=True).stdout.decode()
            return ver
        except Exception as e:
            print("Error getting version from ctdb", e)
            return None
