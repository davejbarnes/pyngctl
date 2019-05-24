#!/usr/bin/python

import djargs as args, djlivestatus as ls, subprocess

debug = False
ls.debug = debug
ls.debug_force_fail = False
ls.test_mode = True

if not args.valid:
    print("Invalid parameters specified:")
    for error in sorted(args.errors):
        print("\t",error)
    exit(1)

print("Everything is working!")
for k,v in enumerate(args.validargs.items()):
    print(k,v)

if args.rules_passed and args.djargs_config.enable_rules:
    print("\nRules passed")
if not args.rules_passed and args.djargs_config.enable_rules:
    print("\nRules failed")
    for errors in args.rule_errors:
        for error in errors:
            print(error)


def find_mode() -> str:
    """Figure out which mode has been specified"""
    modes = ["down", "ack", "dn", "en", "dc", "ec"]
    for arg in args.validargs:
        if str(arg) in modes:
            return arg
    return "down"

print("Mode is", find_mode(),"\n")

print("** Downtime hosts **")
result = ls.downtime_hosts(["dc1web01", "dc1web02"], 1558681200, 1558682200, "Testing")
print("Result: ",result,"\n")

print("** Downtime services on hosts **")
result = ls.downtime_hostsservices(["dc1web01"], ["uptime_status", "ntp_time"], 1558681200, 1558682200, "Testing")
print("Result: ",result,"\n")

print("** Acknowledge host problems **")
result = ls.ack_hostsproblem(["dc1web1"],"comment")
print("Result: ",result,"\n")

print("** Acknowledge service problems **")
result = ls.ack_hostsservicesproblem(["dc1web1"], ["uptime_status"], "comment")
print("Result: ",result,"\n")

print("** Disable host checks **")
result = ls.dis_hostscheck(["dc01web1"])
print("Result: ",result,"\n")

print("** Enable host checks **")
result = ls.en_hostscheck(["dc01web1"])
print("Result: ",result,"\n")

print("** Disable host notifications **")
result = ls.dis_hostsnotifications(["dc01web1"])
print("Result: ",result,"\n")

print("** Enable host notifications **")
result = ls.en_hostsnotifications(["dc01web1"])
print("Result: ",result,"\n")

print("** Disable service checks **")
result = ls.dis_hostsservicescheck(["dc01web1"], ["uptime_status", "ntp_time"])
print("Result: ",result,"\n")

print("** Enable service checks **")
result = ls.en_hostsservicescheck(["dc01web1"], ["uptime_status", "ntp_time"])
print("Result: ",result,"\n")

print("** Disable service notifications **")
result = ls.dis_hostsservicesnotifications(["dc01web1"], ["uptime_status", "ntp_time"])
print("Result: ",result,"\n")

print("** Enable service notifications **")
result = ls.en_hostsservicesnotifications(["dc01web1"], ["uptime_status", "ntp_time"])
print("Result: ",result,"\n")