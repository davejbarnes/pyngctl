#!/usr/bin/python

import djargs as args, djlivestatus as ls, subprocess

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
    #if args.validargs["-mode"]:
    #    return args.validargs["-mode"][0]
    modes = ["down", "ack", "dn", "en", "dc", "ec"]
    for arg in args.validargs:
        if str(arg) in modes:
            return arg
    # default to down mode
    return "down"

print("Mode is", find_mode())
