"""config required by djlivestatus library"""

from os import getlogin
current_user = getlogin()

env_livestatus='/var/spool/nagios/cmd/live'         # live status socket for LQL queries
env_cmdpipe='/var/log/nagios/rw/nagios.cmd'         # nagios command pipe