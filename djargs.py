
import sys, re, subprocess, conf.djargs_config as djargs_config
from collections import defaultdict

def validate_type(pvalue: str, ptype: str) -> bool:
    if ptype == 'string' and isinstance(pvalue, str):
        return True
    try:
        if ptype == 'int' and isinstance(int(pvalue), int):
            return True
    except:
        return False
    try:
        if ptype == 'float' and isinstance(float(pvalue), float):
            return True
    except:
        return False

    if ptype == 'date':
        try:
            subprocess.check_output(['date', '-d ' + pvalue, '+%s'], stderr=subprocess.STDOUT)[0:-1]
            return True
        except:
            return False

    if ptype == 'none':
        if pvalue == ptype:
            return True
    return False


# def dedupe_list(input_list: list) -> list:
#     output_list = []
#     for item in sorted(input_list):
#         if item not in output_list:
#             output_list.append(item)
#     return output_list


def custom_join(inlist: list, join_string: str) -> str:
    out_string = ''
    for item in inlist:
        if out_string == '':
            out_string += item
        else:
            out_string += join_string + item
    return out_string


def parse(parameters: dict) -> [dict, bool, list]:
    accepted_parameters = defaultdict(list)
    arguments = sys.argv
    valid_parameters = True
    error_list = []

    for index, arg in enumerate(arguments):
        if index == 0:
            continue

        try:
            current_switch = arg[0:arg.index("=")]
            current_value = arg[arg.index("=")+1:]
        except:
            current_switch = arg
            current_value = 'none'  # this is bad

        if current_switch not in parameters:
            error = current_switch + " is not valid"
            error_list.append(error)
            valid_parameters = False
            continue

        for delim in parameters[current_switch]["delimiter"]:
            current_value = current_value.replace(delim, "¬")

        pattern = re.compile(parameters[current_switch]["regex"])
        for value in current_value.split("¬"):
            pattern_match = pattern.match(str(value))
            try:
                if pattern_match.group() != value:
                    error = current_switch + " '" + value + "' : Pattern partially matches - check your regex?"
                    error_list.append(error)
                    valid_parameters = False
            except:
                error = current_switch + " '" + value + "' : Pattern does not match"
                error_list.append(error)
                valid_parameters = False

        for value in current_value.split("¬"):
            if not validate_type(value, parameters[current_switch]["type"]):
                error = current_switch + ' with value ' + value + ' is invalid'
                error_list.append(error)
                valid_parameters = False

        if accepted_parameters[current_switch] != [] and parameters[current_switch]["unique"]:
            error = current_switch + " can only be specified once"
            error_list.append(error)
            valid_parameters = False


        for value in current_value.split("¬"):
            if value not in accepted_parameters[current_switch]:
                accepted_parameters[current_switch].append(value)

    # Checking if a key exists in a defaultdict does weird things
    check_parameters = dict(accepted_parameters)

    for switch in check_parameters:
        for exclusive in parameters[switch]["exclusive_of"]:
            try:
                if check_parameters[exclusive]:
                    error = switch + " should not be specified along with " + exclusive
                    error_list.append(error)
                    valid_parameters = False
            except:
                pass


    for switch in parameters:
        if parameters[switch]["required"]:
            if switch not in accepted_parameters:
                unless_found = False
                if parameters[switch]["required_unless"]:
                    for unless in parameters[switch]["required_unless"]:
                        if unless in accepted_parameters:
                            unless_found = True
                    found_requirements = unless_found
                else:
                    found_requirements = False
            else:
                found_requirements = True
        else:
            continue

        if not found_requirements:
            valid_parameters = False
            if parameters[switch]["required_unless"]:
                error = switch + " (" + parameters[switch]["description"] + ") is required unless one of \"" + custom_join(parameters[switch]["required_unless"], ', ') + "\" is specified"
            else:
                error = switch + " (" + parameters[switch]["description"] + ") is required"
            error_list.append(error)


    for switch in check_parameters:
        found_dependencies = True
        if parameters[switch]["depends"]:
            dependency_found = True
            for dependency in parameters[switch]["depends"]:
                if dependency not in check_parameters:
                    dependency_found = False
                found_dependencies = dependency_found

        if not found_dependencies:
                valid_parameters = False
                error = switch + " (" + parameters[switch]["description"] + ") depends on " + custom_join(parameters[switch]["depends"], 'and') + " also being specified"
                error_list.append(error)


    for switch in parameters:
        if switch not in accepted_parameters:
            if parameters[switch]["default"] != []:
                conflict = False
                for exclusive in parameters[switch]["exclusive_of"]:
                    if switch == exclusive:
                        conflict = True
                if not conflict:
                    accepted_parameters[switch] = parameters[switch]["default"]


    return accepted_parameters, valid_parameters, error_list


def str_to_timestamp(datestring: str) -> int:
    timestamp = subprocess.check_output(['date', '-d ' + datestring, '+%s'], stderr=subprocess.STDOUT)[0:-1]
    return timestamp


def check_rules(switch, rules):
    new_rules = []
    original_rules = []
    errors = []
    for rule in rules:
        regex = "-{0,2}[a-zA-Z0-9]{1,}"
        pattern = re.compile(regex)
        matches = re.findall(pattern, rule)
        if matches == []:
            pass
            #errors.append("INFO: Didn't match any parameters for rule '" + rule + "'")
        for match in matches:
            try:
                test = validargs[match][0]
                newrule = rule.replace(match, str(test))
                newrule = str(validargs[switch][0]) + " " + newrule
                new_rules.append(newrule)
                original_rules.append(rule)
            except:
                errors.append("Can't find rule parameter " + match + " for rule '" + switch + " " + rule + "'")

    
    if new_rules == []:
        return True, errors
    for index, rule in enumerate(new_rules):
        #print("Testing rule", rule)
        try:
            test = eval(rule)
            #print("Test result", test)
            if not test:
                #print("Logging fail")
                errors.append("Rule for '" + switch + "' (" + switch + " " + original_rules[index] + ") failed")
        except:
            errors.append("Unable to process rule '" + rule + "'")
            test = False
    return test, errors


__dj_args__ = parse(djargs_config.parameters)

if djargs_config.date_convert:
    for switch in __dj_args__[0]:
        if djargs_config.parameters[switch]["type"] == "date":
            utime = int(str_to_timestamp(__dj_args__[0][switch][0]))
            __dj_args__[0][switch][0] = utime


validargs = dict(__dj_args__[0])
valid = bool(__dj_args__[1])
errors = list(__dj_args__[2])
rules_passed = True
rule_errors = []

if djargs_config.enable_rules and valid:
    for switch in validargs:
        switch_rules = djargs_config.parameters[switch]["rules"]
        switch_type = djargs_config.parameters[switch]["type"]
        if switch_rules != [] and switch_type != "string":
            rulecheck = check_rules(switch, switch_rules)
            if not rulecheck[0]:
                rules_passed = False
                rule_errors.append(rulecheck[1])

rules_partial = False
if rules_passed and (rule_errors != []):
    rules_partial = True