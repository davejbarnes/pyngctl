#!/usr/bin/python

import djargs as args, djlivestatus as ls, subprocess

if not args.valid:
    print("Invalid parameters specified:")
    for error in sorted(args.errors):
        print("\t",error)
    exit(1)


def find_mode() -> str:
    """Figure out which mode has been specified"""
    modes = ["down", "ack", "dn", "en", "dc", "ec"]
    for arg in args.validargs:
        if str(arg) in modes:
            return arg
    return "down" # default to down mode

