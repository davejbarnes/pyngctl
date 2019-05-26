#!/usr/bin/python

import djargs as args, djlivestatus as ls, subprocess
ls.test_mode = True

if not args.valid:
    print("Invalid parameters specified:")
    for error in sorted(args.errors):
        print("\t",error)
    exit(1)

if not args.rules_passed and args.djargs_config.enable_rules == True:
    print("\nParameter rules not met:")
    for errors in args.rule_errors:
        for error in errors:
            print("\t" + error)
    #exit(1)

if args.rules_partial:
    print("Rules partially failed:")
    for errors in args.rule_errors:
        for error in errors:
            print("\t" + error)


def dedupe_list(input_list: list) -> list:
    output_list = []
    for item in sorted(input_list):
        if item not in output_list:
            output_list.append(item)
    return output_list


def find_mode() -> str:
    """Figure out which mode has been specified"""
    modes = ["down", "ack", "dn", "en", "dc", "ec"]
    for arg in args.validargs:
        if str(arg) in modes:
            return arg
    return "down" # default to down mode


def parameter_exists(param: str) -> bool:
    """Check if a parameter (key) exists in args.validargs[], returns bool"""
    try:
        test = args.validargs[param]
        return True
    except:
        return False


def combine_hosts():
    """Combines all hosts specified by -h and hosts in all hostgroups specified by -H"""
    all_hosts = []
    if parameter_exists('-H'):
        all_hosts = all_hosts + ls.hosts_inhostgroups(args.validargs['-H'])
    if parameter_exists('-h'):
        all_hosts = all_hosts + args.validargs['-h']
    all_hosts = dedupe_list(all_hosts)
    return all_hosts


def str_to_timestamp(datestring: str) -> int:
    timestamp = subprocess.check_output(['date', '-d ' + datestring, '+%s'], stderr=subprocess.STDOUT)[0:-1]
    return timestamp


def start_time() -> int:
    if parameter_exists('-b'):
        if isinstance(args.validargs['-b'][0], int):
            return args.validargs['-b'][0]
        start = str_to_timestamp(args.validargs['-b'][0])
        return int(start)


def end_time(start: int) -> int:
    if parameter_exists('-e'):
        if isinstance(args.validargs['-e'][0], int):
            return args.validargs['-e'][0]
        endtime = str_to_timestamp(args.validargs['-e'][0])
        return int(endtime)
    add_time = 0
    if parameter_exists('-d'):
        add_time = add_time + int(args.validargs['-d'][0]) * 60
    if parameter_exists('-D'):
        hours = int(args.validargs['-D'][0]) * 60 * 60
        add_time = add_time + hours
    return add_time + start


mode = find_mode()


if parameter_exists('-h') and not parameter_exists('-H'):
    if len(args.validargs['-h']) == 1:
        host_for_range = args.validargs['-h'][0]
        try:
            int(host_for_range[-2:])
        except:
            if parameter_exists('-x'):
                range_hosts = []
                range_start = int(args.validargs['-x'][0])
                range_end = int(args.validargs['-y'][0])
                if parameter_exists('-p'):
                    if args.validargs['-p'][0] == 'odd':
                        if range_start %2 == 0:
                            range_start += 1

                    if args.validargs['-p'][0] == 'even':
                            if range_start %2 != 0:
                                range_start += 1
                    for number in range(range_start, range_end + 1, 2):
                        range_hosts.append(host_for_range + str(number).zfill(2))
                else:
                    for number in range(range_start, range_end + 1):
                        range_hosts.append(host_for_range + str(number).zfill(2))

                print(range_hosts)
                args.validargs['-h'] = range_hosts

if parameter_exists('-h') or parameter_exists('-H'):
    ng_hosts = combine_hosts()


if mode == "down":
    ng_start = start_time()
    ng_end = end_time(ng_start)
    ng_comment = args.validargs['-c'][0]
    
    if parameter_exists('-s'):
        ng_services = args.validargs['-s']
        result = ls.downtime_hostsservices(ng_hosts, ng_services, ng_start, ng_end, ng_comment)
    else:
        result = ls.downtime_hosts(ng_hosts, ng_start, ng_end, ng_comment)


if mode == "ack":
    sticky = True if parameter_exists('-k') else False
    notify = True if parameter_exists('-n') else False
    ng_comment = args.validargs['-c'][0]
    if parameter_exists('-s'):
        ng_services = args.validargs['-s']
        result = ls.ack_hostsservicesproblem(ng_hosts, ng_services, ng_comment, sticky, notify)
    else:
        result = ls.ack_hostsproblem(ng_hosts, ng_comment, sticky, notify)


if mode == "dn":
    if parameter_exists('-s'):
        ng_services = args.validargs['-s']
        result = ls.dis_hostsservicesnotifications(ng_hosts, ng_services)
    else:
        result = ls.dis_hostsnotifications(ng_hosts)


if mode == "en":
    if parameter_exists('-s'):
        ng_services = args.validargs['-s']
        result = ls.en_hostsservicesnotifications(ng_hosts, ng_services)
    else:
        result = ls.en_hostsnotifications(ng_hosts)


if mode == "dc":
    if parameter_exists('-s'):
        ng_services = args.validargs['-s']
        result = ls.dis_hostsservicescheck(ng_hosts, ng_services)
    else:
        result = ls.dis_hostscheck(ng_hosts)


if mode == "ec":
    if parameter_exists('-s'):
        ng_services = args.validargs['-s']
        result = ls.en_hostsservicescheck(ng_hosts, ng_services)
    else:
        result = ls.en_hostscheck(ng_hosts)



if result[0]:
    print("All commands completed successfully")
    for hostname in sorted(result[1]):
        print(hostname + ";" + result[1][hostname])
    exit(0)
else:
    print("One or more commands failed")
    for hostname in sorted(result[1]):
        print(hostname, ";", result[1][hostname])
    exit(1)    