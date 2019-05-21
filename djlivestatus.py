"""library for interacting with Nagios / MK Livestatus"""

import conf.djlivestatus_config as config, socket, re
from time import time

def livestatus_query(query: list = ["GET status"]) -> str:      # done?
    """
    Executes a Livestatus query and returns the result

    The query should be provided as a list of Livestatus Query Language statements
    which will be combined in the order they are supplied
    """
    # This was roughly lifted from mathias-kettner.com - live_example.py
    # original version allowed tcp or unix socket, for the latter automatic
    # detection by OMD config.  I assume a configured path for a unix socket.
    ls_query = ""
    for statement in query:
        ls_query += statement + "\n"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(config.env_livestatus)
    sock.sendall(ls_query)
    sock.shutdown(socket.SHUT_WR)
    chunks = []
    while len(chunks) == 0 or chunks[-1] != "":
        chunks.append(sock.recv(4096))
    sock.close()
    reply = "".join(chunks)
    sock.close()
    return reply


def nagios_command(command: str, confirm_query: list = [], expect_regex: str = ".*",
                    retry_command: int = 3, retry_confirm: int = 3) -> [bool, str]:         # done?
    """Wraps and executes a raw Nagios external command, optionally confirming the result"""
    utimestamp = str(int(time.time()))
    ls_command="COMMAND [" + str(utimestamp) + "] "
    ls_command += command
    ls_command += "\n "

    command_count = 0
    confirm_count = 0
    pattern = re.compile(expect_regex)
    while command_count <= retry_command:
        cmd_file = open(config.env_cmdpipe, "a")
        cmd_file.write(ls_command)
        cmd_file.close()

        if confirm_query == []:
            return True, "command_unconfirmed" 
        while confirm_count <= retry_confirm:
            reply = livestatus_query(confirm_query)
            pattern_match = pattern.match(reply)
            try:
                if pattern_match.group():
                    return True, reply
            except:
                pass
            confirm_count += 1
        command_count += 1

    return False, "command_failed"


def hosts_inhostgroups(hostgroups: list) -> list:           # done?
    """Returns a list of hosts in the given hostgroup"""
    query = []
    query.append("GET hostsbygroup")
    for count, hostgroup in enumerate(hostgroups):
        hostgroup = str(hostgroup)
        query.append("Filter: hostgroup_name = " + hostgroup)
    query.append("Or: " + str(count + 1))
    query.append("Columns: name")
    reply = livestatus_query(query)
    if ";" in reply:
        return reply.split(";")
    return reply


def host_exists(hostname: str) -> bool:
    query = []
    query.append("GET hosts")
    query.append("Filter: name = " + hostname)
    query.append("Columns: name")
    reply = livestatus_query(query)
    if reply == hostname:
        return True
    return False


def hostservice_exists(hostname: str, service: str) -> bool:
    query = []
    query.append("GET services")
    query.append("Filter: host_name = " + hostname)
    query.append("Filter: description = " + service)
    query.append("Columns: host_name")
    reply = livestatus_query(query)
    if reply == hostname:
        return True
    return False


def host_problem_exists(hostname: str, state: int) -> bool:
    query = []
    query.append("GET hosts")
    query.append("Filter: name = " + hostname)
    query.append("Filter: state >= 1")
    query.append("Columns: name")
    reply = livestatus_query(query)
    if reply == hostname:
        return True
    return False


def hostservice_problem_exists(hostname: str, service: str, state: int) -> bool:
    query = []
    query.append("GET services")
    query.append("Filter: host_name = " + hostname)
    query.append("Filter: description = " + service)
    query.append("Filter: state >= 1")
    query.append("Columns: host_name")
    reply = livestatus_query(query)
    if reply == hostname:
        return True
    return False


def downtime_hosts(hostnames: list, begintime: int, endtime: int, comment: str,
                    username: str = config.current_user) -> [bool, dict]:       # done?
    """Add downtime for host(s), returns bool indicating if all were
    successful and dict of 'hostname' and their entry IDs or status message"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        command = "SCHEDULE_HOST_DOWNTIME;" + hostname + ";" 
        command += str(begintime) + ";" + str(endtime) + ";1;0;0;" + username + ";" + comment
        confirm = []
        confirm.append("GET downtimes")
        confirm.append("Filter: author = " + username)
        confirm.append("Filter: host_name = " + hostname)
        confirm.append("Filter: end_time = " + str(endtime))
        confirm.append("Filter: start_time = " + str(begintime))
        confirm.append("Columns: id")
        expect = "\d{1,}"

        result = nagios_command(command, confirm, expect)
        if not result[0]:
            all_good = False
        results[hostname] = result[1]
    
    return all_good, results


def downtime_hostsservices(hostnames: list, services: list, begintime: int, endtime: int,
                            comment: str, username: str = config.current_user) -> bool:
    """Add downtime for service(s) on host(s), returns bool indicating if all were
    successful and dict of 'hostname_service' and their entry IDs or status message"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        for service in services:
            service = str(service)
            command = "SCHEDULE_SVC_DOWNTIME;" + hostname + ";" + service + ";"
            command += str(begintime) + ";" + str(endtime) + ";1;0;0;" + username + ";" + comment
            confirm = []
            confirm.append("GET downtimes")
            confirm.append("Filter: author = " + username)
            confirm.append("Filter: host_name = " + hostname)
            confirm.append("Filter: service_description = " + service)
            confirm.append("Filter: end_time = " + str(endtime))
            confirm.append("Filter: start_time = " + str(begintime))
            confirm.append("Columns: id")
            expect = "\d{1,}"

            result = nagios_command(command, confirm, expect)
            if not result[0]:
                all_good = False
            results[hostname + "_" + service] = result[1]
    
    return all_good, results


def ack_hostsproblem(hostnames: list, comment: str, sticky: bool = False, notify: bool = False) -> bool:
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        command = "ACKNOWLEDGE_HOST_PROBLEM;" + hostname + ";" + str(int(sticky)) + ";" + str(int(notify))
        command += ";1;" + username + ";" + comment
        confirm = []
        confirm.append("GET hosts")
        confirm.append("Filter: name = " + hostname)
        confirm.append("Filter: state >= 1")
        confirm.append("Columns: name")
        expect = hostname

        result = nagios_command(command, confirm, expect)
        if not result[0]:
            all_good = False
        results[hostname] = result[1]
    
    return all_good, results


def ack_hostsservicesproblem(hostnames: list, services: list, comment: str, sticky: bool = False, notify: bool = False) -> bool:
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        for service in services:
            service = str(service)
            command = "ACKNOWLEDGE_HOST_PROBLEM;" + hostname + ";" + service + ";" + str(int(sticky)) + ";"
            command += str(int(notify)) + ";1;" + username + ";" + comment
            confirm = []
            confirm.append("GET services")
            confirm.append("Filter: host_name = " + hostname)
            confirm.append("Filter: description = " + service)
            confirm.append("Filter: state >= 1")
            confirm.append("Columns: name")
            expect = hostname

            result = nagios_command(command, confirm, expect)
            if not result[0]:
                all_good = False
            results[hostname] = result[1]
    
    return all_good, results


def dis_hostscheck(hostname: list) -> bool:
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        command = ""
        # DISABLE_HOST_CHECK;$targethost\n


def dis_hostsservicescheck(hostname: list, service: list) -> bool:
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        for service in services:
            service = str(service)
            command = ""
            # DISABLE_SVC_CHECK;$targethost;$service\n


def dis_hostsnotifications(hostname: list) -> bool:
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        command = ""
        # DISABLE_HOST_NOTIFICATIONS;$targethost\n


def dis_hostsservicescheck(hostname: list, service: list) -> bool:
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        for service in services:
            service = str(service)
            command = ""
            # DISABLE_SVC_NOTIFICATIONS;$targethost;$service\n

