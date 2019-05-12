#!/usr/bin/python

import djargs, djargs_config as config

validate_args = djargs.parse(config.parameters)

if not validate_args[1]:
    print("Invalid parameters specified:")
    for error in sorted(validate_args[2]):
        print("\t",error)
    exit(1)

print("All is good! We got:\n")

for k, v in sorted(validate_args[0].items()):
    if k[0] == '-':
        print(k, "-->", v)
