"""configuration file required by djargs, defines the allowed parameters"""
#
# the key is the parameter, eg -p
# valid 'fields' are:
#
#   description : string, description used in help REQUIRED
#   regex : a regex pattern to match when type is "string", optional (default ".*" except for type 'date' - see below)
#   type : string, one of "string, int, float, date", optional (default "none")
#   delimiter: list of strings used to delimiter multiple values for the field, optional, (default no delimmiter)
#   required : bool, whether the parameter is required. optional (default False)
#   required_unless : list, negate requirement if *one or more* other parameters are specified (implies 'required = true'), optional
#   depends : list, parameters which must *all* also be specified with this one, optional
#   exclusive_of : lits, parameters *any* of which must not also be specified, optional
#   unique : bool, whether the parameter must be specified at most once. optional (default False)
#   help : string, text used in extended help REQUIRED
#   rules : list of strings, each of which will be evaluated as ("parameter value" rule), eg "< -a" would indicate the value of parameter should be less than the value of -a


#   the simplest parameter takes this form:

#   "-p": {
#       "description": "example parameter",
#       "help": "help for example paramter"
#   }


##  edit below here  ##

# default regex for date type parameters. setting "regex" field overrides for an individual parameter
# combinations of "yyyy-mm-dd", "dd/mm/yyy" hh:mm", "9am", "9pm" (space between date and time)
# "last friday 12am", "11am tomorrow", "10:30 next weds" etc
regex_date = "(((20[1-9][0-9](-|/)[01][0-9](-|/)[0-3][0-9]|[0-3][0-9]/[01][0-9]/20[1-9][0-9]) ([0-2]?[0-9]:[0-5][0-9]|[0-2]?[0-9]:[0-5][0-9]|[01]?[1-2][ap]m|[1-9][ap]m|1[0-2][ap]m|[0-2]?[0-9]:[0-5][0-9]))|(([0-2]?[0-9]:[0-5][0-9]|[0-2]?[0-9]:[0-5][0-9]|[01]?[1-2][ap]m|[1-9][ap]m|1[0-2][ap]m|[0-2]?[0-9]:[0-5][0-9]) (20[1-9][0-9](-|/)[01][0-9](-|/)[0-3][0-9]|[0-3][0-9]/[01][0-9]/20[1-9][0-9]))|(20[1-9][0-9](-|/)[01][0-9](-|/)[0-3][0-9]|[0-3][0-9]/[01][0-9]/20[1-9][0-9])|[0-2]?[0-9]:[0-5][0-9]|[01]?[1-2][ap]m|[1-9][ap]m|1[0-2][ap]m|[0-2]?[0-9]:[0-5][0-9])|(([0-2]?[0-9]:[0-5][0-9]|[01]?[1-2][ap]m|[1-9][ap]m|1[0-2][ap]m|[0-2]?[0-9]:[0-5][0-9])?(( )?next |( )?last |( )?Next |( )?Last )?(monday( )?|Monday( )?|mon( )?|Mon( )?|tuesday( )?|Tuesday( )?|tue( )?|tues( )?|Tue( )?|Tues( )?|wednesday( )?|Wednesday( )?|wed( )?|Wed( )?|thursday( )?|Thursday( )?|thu( )?|thur( )?|Thu( )?|Thur( )?|friday( )?|Friday( )?|fri( )?|Fri( )?|saturday( )?|Saturday( )?|sat( )?|Sat( )?|sunday( )?|Sunday( )?|sun( )?|Sun( )?|week( )?)|([0-2]?[0-9]:[0-5][0-9]|[01]?[1-2][ap]m|[1-9][ap]m|1[0-2][ap]m|[0-2]?[0-9]:[0-5][0-9])?( ?tomorrow| ?Tomorrow| ?today| ?Today)( )?)([0-2]?[0-9]:[0-5][0-9]|[01]?[1-2][ap]m|[1-9][ap]m|1[0-2][ap]m|[0-2]?[0-9]:[0-5][0-9])?"

# IMPORTANT:    enabling parameter rules is a potential security issue
#               rules make us of eval(), use only if you can trust this config file
#               "rules": ['rm -rf ~']" or similar is not desirable!
#               use: "< -a" would indicate the value of parameter should be less than the value of -a
enable_rules = True

# Enabling date_convert will update validated parmeters of type "date" to a unix timestamp
date_convert = True


parameters={
    "-h": {
        "description": "hostname",
        "regex": "^(dc1|dc2)[a-zA-Z0-9\-]*\d{2,}$",
        "type": "string",
        "required_unless": ['-H'],
        # commnent
        "delimiter": [',', ' '],
        "help": "a valid hostname which exists in the Nagios instance"
    },
    "-H": {
        "description": "hostgroup",
        "regex": "[a-zA-Z\-_]+$",
        "type": "string",
        "delimiter": [',', ' '],
        "required_unless": ['-h'],
        "help": "a valid hostgroup which exists in the Nagios instance"
    },
    "-s": {
        "description": "service description",
        "regex": "[a-zA-Z0-9\-_]+$",
        "type": "string",
        "delimiter": [',', ' '],
        "help": "the service description for a service which exists in the Nagios instance"
    },
    "-b": {
        "description": "start date/time",
        "type": "date",
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
    "-d": {
        "description": "duration minutes",
        "type": "float",
        "unique": True,
        "exclusive_of": ['-e', "ack", "dn", "en", "dc", "ec"],
        "required_unless": ['-e', '-D', "ack", "dn", "en", "dc", "ec"],
        "rules": ['> 1'],
        "help": "for adding a downtime, the duration of the entry in minutes"
    },
    "-D": {
        "description": "duration hours",
        "type": "float",
        "unique": True,
        "exclusive_of": ['-e', "ack", "dn", "en", "dc", "ec"],
        "required_unless": ['-e', '-d', "ack", "dn", "en", "dc", "ec"],
        "rules": ['> 0', '< 99'],
        "help": "for adding a downtime, the duration of the entry in hours"
    },
    "-c": {
        "description": "comment",
        "type": "string",
        "unique": True,
        "required_unless": ["dn", "en", "dc", "ec"],
        "help": "a comment is required when adding downtime entries or acknowledgements"
    },
    "-q": {
        "description": "quiet",
        "unique": True,
        "help": "set output to minimum"
    },
    # "-mode": {
    #     "description": "mode",
    #     "type": "string",
    #     "regex": "down|ack|dn|en|dc|ec",
    #     "unique": True,
    #     "exclusive_of": ["ack", "dn", "en", "dc", "ec", "down"],
    #     "help": "set mode"
    # },
    "down": {
        "description": "down mode",
        "unique": True,
        "exclusive_of": ["ack", "dn", "en", "dc", "ec", "-mode"],
        "help": "set mode to downtime"
    },
    "ack": {
        "description": "ack mode",
        "unique": True,
        "exclusive_of": ["down", "dn", "en", "dc", "ec", "-mode"],
        "help": "set mode to acknowledge"
    },
    "dn": {
        "description": "disable notifications mode",
        "unique": True,
        "exclusive_of": ["down", "ack", "en", "dc", "ec", "-mode"],
        "help": "set mode to acknowledge"
    },
    "en": {
        "description": "enable notifications mode",
        "unique": True,
        "exclusive_of": ["down", "dn", "ack", "dc", "ec", "-mode"],
        "help": "set mode to acknowledge"
    },
    "dc": {
        "description": "disable checks mode",
        "unique": True,
        "exclusive_of": ["down", "dn", "en", "ack", "ec", "-mode"],
        "help": "set mode to acknowledge"
    },
    "ec": {
        "description": "enable checks mode",
        "unique": True,
        "exclusive_of": ["down", "dn", "en", "dc", "ack", "-mode"],
        "help": "set mode to acknowledge"
    },
}

##  edit above here  ##
##  do not edit below here  ##

# Set defaults
for part in parameters:

    try:
        test = parameters[part]["type"]
    except:
        parameters[part]["type"] = "none"

    try:
        test = parameters[part]["required"]
    except:
        try:
            test = parameters[part]["required_unless"]
            parameters[part]["required"] = True
        except:
            parameters[part]["required"] = False

    try:
        test = parameters[part]["required_unless"]
    except:
        parameters[part]["required_unless"] = []

    try:
        test = parameters[part]["depends"]
    except:
        parameters[part]["depends"] = []

    try:
        test = parameters[part]["exclusive_of"]
    except:
        parameters[part]["exclusive_of"] = []

    try:
        test = parameters[part]["unique"]
    except:
        parameters[part]["unique"] = False

    try:
        test = parameters[part]["delimiter"]
    except:
        parameters[part]["delimiter"] = []

    try:
        test = parameters[part]["regex"]
    except:
        if parameters[part]["type"] == 'date':
            parameters[part]["regex"] = regex_date
        else:
            parameters[part]["regex"] = ".*"

    try:
        test = parameters[part]["rules"]
    except:
        parameters[part]["rules"] = []