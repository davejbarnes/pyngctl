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

Acceptable parameters are defined as a Dictionary of Dictionaries, where the primary Dictionary's key is a parameter, and the secondary dictionary has keys specifying the parameter properties. It is **not** json.

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

   * string, description of the parameter
   * required
   * default: none
   * ```"description": "a string",```
* `help`

   * string, help to be displayed for the parameter
   * required
   * default: none
   * ```"help": "a string",```
* `type`

   * parameter type, one of: string, int, float, date, none
   * default: none
   * ```"type": "string",```
   * ```"type": "int",```
   * ```"type": "float",```
   * ```"type": "date",```
* `regex`

   * regex pattern which must be matched
   * default '.*'
   * ```"regex": "regex expression",```
   * ```"regex": "^dc(1|2)",```

* `delimiter`

   * list of allowed delimiters
   * default: none
   * ```"delimiter": [","],```
* `unique`

   * bool, whether a parameter may be only specified once
   * default: False
   * ```"unique": True,```
* `required`

   * bool, whether a parameter must be specified
   * default: False
   * ```"required": True,```
* `required_unless`

    * list of other parmaters which negate a parameter requirement
    * default: none
    * ```"required_unless": ["-u"],```
* `exclusive_of`

    * list of other parameters which must not be speficied with the current one
    * default: none
    * ```"exclusive_of": ["-e"],```
* `depends`

    * list of other parameters which must also be speficied with the current one
    * default: none
    * ```"depends": ["-d"],```
* `rules`

    * list of rules applied to the parameter
    * only valid for types "int", "float" and "date" (date if `date_convert = True` is configured)
    * default: none
    * ```"rules": ["> -m", "< 100"],```
* `default`

    * default value for the parameter, respectful of other criteria
    * default: none
    * ```"default": "default string value",```
    * ```"default": 1,```
    * ```"default": 3.141,```
    * ```"default": "Now,```

##### Examples

Have a look at the djargs_config.py file in the conf dir in this repo, if you're familiar with Nagios it will help but isn't needed - it uses all the parameter options.

Most of the options are hopefully obvious in their use, but here are a few examples from the pyngctl config explained for clarity.

```python
"-b": {
        "description": "start date/time",
        "type": "date",
        "default": ['Now'],
        "unique": True,
        "rules": ['< -e'],
        "exclusive_of": ["ack", "dn", "en", "dc", "ec"],
        "help": "for adding a downtime, the start date/time of the entry"
    },
"-e": {
        "description": "end date/time",
        "type": "date",
        "unique": True,
        "exclusive_of": ['-d', '-D', "ack", "dn", "en", "dc", "ec"],
        "required_unless": ['-D', '-d', "ack", "dn", "en", "dc", "ec"],
        "rules": ['> -b'],
        "help": "for adding a downtime, the end date/time of the entry"
    },
```
Here we have two parameters, `-b` a begin date/time, and `-e` an end date/time.  They both have the required `"description"` and `"help"` options.  Their types are both `"date"` and as no `"regex"` is specified, the default `regex_date` will be used as part of validating the user input.  Both parmaters are `"unique"` so may only be specified once on the command line.

`-b` is not required, but it has a default value of `["Now"]` which is a valid date/time string.  However it won't be applied if it would contradict other options, such as the following.

Both `-b` and `-e` have the `"exclusive_of"` option set, so if any of the options listed there are also present validation will fail.  `-e` also has the `"required_unless"` option set.  This means it must be specified unless any one of parameters listed is specified.

Finally the `"rules"` option is set for both parameters.  In this case it relies on the configuration option `date_convert = True` which converts date/time parameters to unix timestamps which can then be compared.

for `-e` we have the rule `'> -b'`
   * `-b` will be replaced with the value of `-b`
   * the value of `-e` will then be evaluated using the resulting rule

