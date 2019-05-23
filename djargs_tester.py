#!/usr/bin/python

import djargs as args, djlivestatus as ls, subprocess

debug = True
ls.debug = debug

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

ls.debug_force_fail = False
ls.test_mode = True

result = ls.dis_hostscheck(["dc01web01"])
print("Result: ",result,"\n")

result = ls.en_hostscheck(["dc01web01"])
print("Result: ",result,"\n")

result = ls.downtime_hosts(["dc01web01"], 1558681200, 1558682200, "Testing")
print("Result: ",result,"\n")