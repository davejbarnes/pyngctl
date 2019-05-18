#!/usr/bin/python

import djargs as args

if not args.valid:
    print("Invalid parameters specified:")
    for error in sorted(args.errors):
        print("\t",error)
    exit(1)

print("Everything is working!")
for k,v in enumerate(args.args.items()):
    print(k,v)

if args.rules_passed and args.djargs_config.enable_rules:
    print("\nRules passed")
if not args.rules_passed and args.djargs_config.enable_rules:
    print("\nRules failed")
    for errors in args.rule_errors:
        for error in errors:
            print(error)
