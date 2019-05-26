# djargs
## Description
djargs is a module for parsing command line arguments

It is designed to offload parameter validation processing as much as possible, and comprises of the module and a configuration file.

The configuration file defines the parameters which can be accepted along with certain criteria and rules which must or should be met.
This should allow the consumer to assume that valid parameters have been provided and proceed accordingly without further processing.

## Conguration file
#### Configuration Options
* `enable_rules` enables processing parameter rules
* `date_convert` enables converting date/time parameters to unix timestamps during processing

#### Specifying parameters
