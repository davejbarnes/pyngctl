# djargs
## Description
djargs is a module for parsing command line arguments

It is designed to offload parameter validation processing as much as possible, and comprises of the module and a configuration file.

The configuration file defines the parameters which can be accepted along with certain criteria and rules which must or should be met.
This should allow the consumer to assume that valid parameters have been provided and proceed accordingly without further processing.

When imported it will import the configuration file and process the command line arguments and be ready to use without any function being called.

Example:
```python
import djargs as args
if args.valid:
    ...stuff

```
## Conguration file
#### Configuration Options
* `enable_rules = bool` enables processing parameter rules
* `date_convert = bool` enables converting date/time parameters to unix timestamps during processing

#### Specifying parameters
Parameters can be any form, such as '`-t`' or '`t`', but to provide a value they must be expressed as '`-t=value`' or '`t=value`'.  More specifically '=' is the delimiter between a parameter and it's value. '`-t value`' etc is not valid.

Acceptable parameters are defined as a Dictionary of Dictionaries, where the primary Dictionary's key is a parameter, and the secondary dictionary has keys specifying the parameter properties.

Example:
```python
parameters = {
    "-s" : {
        "description": "start time",
        "type": "date",
        "help": "The time to start doing the thing"
    },
    "-e" : {
        "description": "end time",
        "type": "date",
        "help": "The time to stop doing the thing"
    }
}
```
##### Parameter properties
* `description`

   * description of the parameter
   * a string
   * required
* `help`

   * help to be displayed for the parameter
   * a string
   * required
* `type`

   * parameter type, one of: string, int, float, date, none
   * default: none
* `regex`
* `delimiter`
* `unique`
* `required`
* `required_unless`
* `exclusive_of`
* `depends`
* `rules`
* `default`
