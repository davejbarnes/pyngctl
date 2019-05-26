"""library for interacting with Nagios / MK Livestatus"""

import conf.djlivestatus_config as config, socket, re, time
debug=False  # set djlivestatus.debug = True in importing script to use
debug_force_fail = False # set djlivestatus.debug_force_fail = True in importing script to use
test_mode = False # set djlivestatus.test_mode = True in importing script to use

def dec_debug_true_false(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        if debug:
            if debug_force_fail:
                return False
            return True
        return wrapper


def livestatus_query(query: list = ["GET status"]) -> str:
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
    if debug:
        print("DEBUG(livestatus_query):", ls_query)
    if test_mode:
        if debug_force_fail:
                return "not_expected"
        return "expected_result"
    try:
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
    except:
        return 'socket_not_found'

def nagios_command(command: str, confirm_query: list = [], expect_regex: str = ".*",
                    retry_command: int = 3, retry_confirm: int = 3) -> [bool, str]:
    """Wraps and executes a raw Nagios external command, optionally confirming the result"""
    # provide command as "NAGIOS_EXTERNAL_COMMAND;param1;param2;etc"
    utimestamp = str(int(time.time()))
    ls_command="COMMAND [" + str(utimestamp) + "] "
    ls_command += command
    ls_command += "\n "
    print(ls_command)
    command_count = 0
    pattern = re.compile(expect_regex)
    while command_count <= retry_command and test_mode == False:
        confirm_count = 0
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
    if debug or test_mode:
        if debug_force_fail:
            debug_query = "not_expected"
        debug_query = "expected_result"
    if debug:
        print("DEBUG(nagios_command):", command)
        print("DEBUG(nagios_command):", confirm_query)
    if test_mode:
        if debug_query == "not_expected":
            return False, debug_query
        return True, debug_query

    return False, "command_failed"


def hosts_inhostgroups(hostgroups: list) -> list:
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
    if test_mode:
        if debug_force_fail:
            return []
        return ['dc1web01', 'dc1web02', 'dc1web03']

    return reply


def host_exists(hostname: str) -> bool:
    """Returns a bool indicating whether a hostname exists"""
    query = []
    query.append("GET hosts")
    query.append("Filter: name = " + hostname)
    query.append("Columns: name")
    reply = livestatus_query(query)
    if test_mode:
        if debug_force_fail:
            return False
        return True
    if reply == hostname:
        return True
    return False


def hostservice_exists(hostname: str, service: str) -> bool:
    """Returns a bool indicating whether a service on a hostname exists"""
    query = []
    query.append("GET services")
    query.append("Filter: host_name = " + hostname)
    query.append("Filter: description = " + service)
    query.append("Columns: host_name")
    reply = livestatus_query(query)
    if test_mode:
        if debug_force_fail:
            return False
        return True
    if reply == hostname:
        return True
    return False


def host_problem_exists(hostname: str) -> bool:
    """Returns a bool indicating whether a hostname is in a problem state"""
    query = []
    query.append("GET hosts")
    query.append("Filter: name = " + hostname)
    query.append("Filter: state >= 1")
    query.append("Columns: name")
    reply = livestatus_query(query)
    if test_mode:
        if debug_force_fail:
            return False
        return True
    if reply == hostname:
        return True
    return False


def hostservice_problem_exists(hostname: str, service: str) -> bool:
    """Returns a bool indicating whether a service on a hostname is in a problem state"""
    query = []
    query.append("GET services")
    query.append("Filter: host_name = " + hostname)
    query.append("Filter: description = " + service)
    query.append("Filter: state >= 1")
    query.append("Columns: host_name")
    reply = livestatus_query(query)
    if test_mode:
        if debug_force_fail:
            return False
        return True
    if reply == hostname:
        return True
    return False


def downtime_hosts(hostnames: list, begintime: int, endtime: int, comment: str,
                    username: str = config.current_user) -> [bool, dict]:
    """Add downtime for host(s), returns bool indicating if all were
    successful and dict of 'hostname' and their entry IDs or status message"""
    results = {}
    all_good = True
    for hostname in hostnames:
        if host_exists(hostname):
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
        else:
            all_good = False
            results[hostname] = "host_for_downtime_host_not_found"
    
    return all_good, results


def downtime_hostsservices(hostnames: list, services: list, begintime: int, endtime: int,
                            comment: str, username: str = config.current_user) -> [bool, dict]:
    """Add downtime for service(s) on host(s), returns bool indicating if all were
    successful and dict of 'hostname_service' and their entry IDs or status message"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            for service in services:
                service = str(service)
                if hostservice_exists(hostname, service):
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
                    results[hostname + ";" + service] = result[1]
                else:
                    all_good = False
                    results[hostname + ";" + service] = "host_service_for_downtime_service_not_found"
        else:
            all_good = False
            results[hostname + ";failed_host_check_before_services"] = "host_for_services_not_found"


    return all_good, results


def ack_hostsproblem(hostnames: list, comment: str, sticky: bool = False, notify: bool = False,
                    username: str = config.current_user) -> [bool, dict]:
    """Acknowledge a host problem, optionally set 'sticky' and whether to notify"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            if host_problem_exists(hostname):
                command = "ACKNOWLEDGE_HOST_PROBLEM;" + hostname + ";" + str(int(sticky)) + ";" + str(int(notify))
                command += ";1;" + username + ";" + comment
                confirm = []
                confirm.append("GET hosts")
                confirm.append("Filter: name = " + hostname)
                confirm.append("Filter: state >= 1")
                confirm.append("Filter: acknowledged = 1")
                confirm.append("Columns: name")
                expect = hostname
                result = nagios_command(command, confirm, expect)
                if not result[0]:
                    all_good = False
                results[hostname] = result[1]
            else:
                all_good = False
                results[hostname] = "host_problem_not_found"
        else:
            all_good = False
            results[hostname] = "host_for_host_problem_not_found"

    return all_good, results


def ack_hostsservicesproblem(hostnames: list, services: list, comment: str, sticky: bool = False, 
                            notify: bool = False, username: str = config.current_user) -> [bool, dict]:
    """Acknowledge a service problem on a host, optionally set 'sticky' and whether to notify"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            for service in services:
                service = str(service)
                if hostservice_exists(hostname, service):
                    if hostservice_problem_exists(hostname, service):
                        service = str(service)
                        command = "ACKNOWLEDGE_SVC_PROBLEM;" + hostname + ";" + service + ";" + str(int(sticky)) + ";"
                        command += str(int(notify)) + ";1;" + username + ";" + comment
                        confirm = []
                        confirm.append("GET services")
                        confirm.append("Filter: host_name = " + hostname)
                        confirm.append("Filter: description = " + service)
                        confirm.append("Filter: state >= 1")
                        confirm.append("Filter: acknowledged = 1")
                        confirm.append("Columns: name")
                        expect = hostname
                        result = nagios_command(command, confirm, expect)
                        if not result[0]:
                            all_good = False
                        results[hostname + ";" + service] = result[1]
                    else:
                        all_good = False
                        results[hostname + ";" + service] = "host_service_problem_not_found"
                else:
                    all_good = False
                    results[hostname + ";" + service] = "service_for_host_service_problem_not_found"
        else:
            all_good = False
            results[hostname + ";failed_host_check_before_services"] = "host_for_host_service_problem_not_found"

    return all_good, results


def dis_hostscheck(hostnames: list) -> [bool, dict]:
    """Disable checks for a host"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            command = "DISABLE_HOST_CHECK;" + hostname
            confirm = []
            confirm.append("GET hosts")
            confirm.append("Filter: name = " + hostname)
            confirm.append("Filter: checks_enabled = 0")
            confirm.append("Columns: checks_enabled")
            expect = "0"
            result = nagios_command(command, confirm, expect)
            if not result[0]:
                all_good = False
            results[hostname] = result[1]
        else:
            all_good = False
            results[hostname] = "host_for_disable_hostcheck_not_found"

    return all_good, results


def dis_hostsservicescheck(hostnames: list, services: list) -> [bool, dict]:
    """Disable checks for a service on a host"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            for service in services:
                service = str(service)
                if hostservice_exists(hostname, service):
                    command = "DISABLE_SVC_CHECK;" + hostname + ";" + service
                    confirm = []
                    confirm.append("GET services")
                    confirm.append("Filter: host_name = " + hostname)
                    confirm.append("Filter: description = " + service)
                    confirm.append("Filter: checks_enabled = 0")
                    confirm.append("Columns: checks_enabled")
                    expect = "0"
                    result = nagios_command(command, confirm, expect)
                    if not result[0]:
                        all_good = False
                    results[hostname + ";" + service] = result[1]
                else:
                    all_good = False
                    results[hostname + ";" + service] = "service_for_disable_service_check_not_found"
        else:
            all_good = False
            results[hostname + ";failed_host_check_before_services"] = "host_for_disable_service_check_not_found"

    return all_good, results


def dis_hostsnotifications(hostnames: list) -> [bool, dict]:
    """Disable notifications for a host"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            command = "DISABLE_HOST_NOTIFICATIONS;" + hostname
            confirm = []
            confirm.append("GET hosts")
            confirm.append("Filter: name = " + hostname)
            confirm.append("Filter: notifications_enabled = 0")
            confirm.append("Columns: notifications_enabled")
            expect = "0"
            result = nagios_command(command, confirm, expect)
            if not result[0]:
                all_good = False
            results[hostname] = result[1]
        else:
            all_good = False
            results[hostname] = "host_for_disable_host_notifications_not_found"

    return all_good, results


def dis_hostsservicesnotifications(hostnames: list, services: list) -> [bool, dict]:
    """Disable notifications for a service on a host"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            for service in services:
                service = str(service)
                if hostservice_exists(hostname, service):
                    command = "DISABLE_SVC_NOTIFICATIONS;" + hostname + ";" + service
                    confirm = []
                    confirm.append("GET services")
                    confirm.append("Filter: host_name = " + hostname)
                    confirm.append("Filter: description = " + service)
                    confirm.append("Filter: notifications_enabled = 0")
                    confirm.append("Columns: notifications_enabled")
                    expect = "0"
                    result = nagios_command(command, confirm, expect)
                    if not result[0]:
                        all_good = False
                    results[hostname + ";" + service] = result[1]
                else:
                    all_good = False
                    results[hostname + ";" + service] = "service_for_disable_service_notifications_not_found"
        else:
            all_good = False
            results[hostname + ";failed_host_check_before_services"] = "host_for_disable_service_notifications_not_found"

    return all_good, results


def en_hostscheck(hostnames: list) -> [bool, dict]:
    """Enable checks for a host"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            command = "ENABLE_HOST_CHECK;" + hostname
            confirm = []
            confirm.append("GET hosts")
            confirm.append("Filter: name = " + hostname)
            confirm.append("Filter: checks_enabled = 1")
            confirm.append("Columns: checks_enabled")
            expect = "1"
            result = nagios_command(command, confirm, expect)
            if not result[0]:
                all_good = False
            results[hostname] = result[1]
        else:
            all_good = False
            results[hostname] = "host_for_enable_host_check_not_found"

    return all_good, results


def en_hostsservicescheck(hostnames: list, services: list) -> [bool, dict]:
    """Enable checks for a service on a host"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            for service in services:
                service = str(service)
                if hostservice_exists(hostname, service):
                    command = "ENABLE_SVC_CHECK;" + hostname + ";" + service
                    confirm = []
                    confirm.append("GET services")
                    confirm.append("Filter: host_name = " + hostname)
                    confirm.append("Filter: description = " + service)
                    confirm.append("Filter: checks_enabled = 1")
                    confirm.append("Columns: checks_enabled")
                    expect = "1"
                    result = nagios_command(command, confirm, expect)
                    if not result[0]:
                        all_good = False
                    results[hostname + ";" + service] = result[1]
                else:
                    all_good = False
                    results[hostname + ";" + service] = "service_for_enable_service_check_not_found"
        else:
            all_good = False
            results[hostname + ";failed_host_check_before_services"] = "host_for_enable_service_check_not_found"

    return all_good, results


def en_hostsnotifications(hostnames: list) -> [bool, dict]:
    """Enable notifications for a host"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            command = "ENABLE_HOST_NOTIFICATIONS;" + hostname
            confirm = []
            confirm.append("GET hosts")
            confirm.append("Filter: name = " + hostname)
            confirm.append("Filter: notifications_enabled = 1")
            confirm.append("Columns: notifications_enabled")
            expect = "1"
            result = nagios_command(command, confirm, expect)
            if not result[0]:
                all_good = False
            results[hostname] = result[1]
        else:
            all_good = False
            results[hostname] = "host_for_enable_host_notifications_not_found"

    return all_good, results


def en_hostsservicesnotifications(hostnames: list, services: list) -> [bool, dict]:
    """Enable notifications for a service on a host"""
    results = {}
    all_good = True
    for hostname in hostnames:
        hostname = str(hostname)
        if host_exists(hostname):
            for service in services:
                service = str(service)
                if hostservice_exists(hostname, service):
                    command = "ENABLE_SVC_NOTIFICATIONS;" + hostname + ";" + service
                    confirm = []
                    confirm.append("GET services")
                    confirm.append("Filter: host_name = " + hostname)
                    confirm.append("Filter: description = " + service)
                    confirm.append("Filter: notifications_enabled = 1")
                    confirm.append("Columns: notifications_enabled")
                    expect = "1"
                    result = nagios_command(command, confirm, expect)
                    if not result[0]:
                        all_good = False
                    results[hostname + ";" + service] = result[1]
                else:
                    all_good = False
                    results[hostname + ";" + service] = "service_for_enable_service_notifications_not_found"
        else:
            all_good = False
            results[hostname + ";failed_host_check_before_services"] = "host_for_enable_service_notifications_not_found"

    return all_good, results
