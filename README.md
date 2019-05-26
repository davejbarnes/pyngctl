# pyngctl
### Rewrite of bash script ngctl

It has three parts:

* A module to parse command line arguments which can validate input in various ways
  
* A module which provides functions to interact with Nagios and Livestatus broker*
  
* A Python script which uses both to provide a command line tool for Nagios and Livestatus

Both modules are agnostic of each other

\* https://mathias-kettner.com

\**Yes, I know argparse exists. I'm learning by doing something familiar in a new language :) .
