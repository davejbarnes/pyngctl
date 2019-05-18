#!/usr/bin/python

import djargs as args, djlivestatus as ls, subprocess

if not args.valid:
    print("Invalid parameters specified:")
    for error in sorted(args.errors):
        print("\t",error)
    exit(1)

def timestamp(timestring: str = "now") -> int:
    shell_output = subprocess.check_output(['date', '-d ' + timestring, '+%s'], stderr=subprocess.STDOUT)[0:-1]
    return int(shell_output)

