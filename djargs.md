# djargs
## Description
djargs is a module for parsing command line arguments

It is designed to offload parameter validation processing as much as possible, and comprises of the module and a configuration file.

The configuration file defines the parameters which can be accepted along with certain criteria and rules which must or should be met.
This should allow the consumer to assume that valid parameters have been provided and proceed accordingly without further processing.

When imported it will import the configuration file and process the command line arguments and be ready to use without any function being called.

## Conguration file
#### Configuration Options
* `enable_rules = bool` enables processing parameter rules
* `date_convert = bool` enables converting date/time parameters to unix timestamps during processing

#### Specifying parameters
Parameters are specified as a Dictionary of Dictionaries, where the primary Dictionary's key is a parameter, and the secondary dictionary has keys specifying the parameter properties.

Example:
`parameters = {
    "-t" : {
        "description": "time",
        "type": "date"
    }
}`

