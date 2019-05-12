import sys, re, subprocess
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


def listtostring(inlist: list, join_string: str) -> str:
    out_string = ''
    for item in inlist:
        if out_string == '':
            out_string += item
        else:
            out_string += " " + join_string + " " + item
    return out_string


def parse(parameters: dict) -> [dict, bool, list]:
    accepted_parameters = defaultdict(list)
    arguments = sys.argv
    valid_parameters = True
    error_list = []

    for index, arg in enumerate(arguments):
        if index == 0:
            continue

        if arg[0] != '-':
            error = arg + " is not a valid switch"
            error_list.append(error)
            valid_parameters = False
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

        for value in current_value.split("¬"):
            if not validate_type(value, parameters[current_switch]["type"]):
                error = current_switch + ' with value ' + value + ' is invalid'
                error_list.append(error)
                valid_parameters = False
                continue

        if accepted_parameters[current_switch] != [] and parameters[current_switch]["unique"]:
            error = current_switch + " can only be specified once"
            error_list.append(error)
            valid_parameters = False
            continue

        for exclusive in parameters[current_switch]["exclusive_of"]:
            if accepted_parameters[exclusive]:
                error = current_switch + " should not be specified along with " + exclusive
                error_list.append(error)
                valid_parameters = False
            else:
                accepted_parameters.pop(exclusive)

        pattern = re.compile(parameters[current_switch]["regex"])

        for value in current_value.split("¬"):
            pattern_match = pattern.match(str(value))
            try:
                if pattern_match.group() != value:
                    error = current_switch + " '" + value + "' : Pattern partially matches - check your regex?"
                    error_list.append(error)
                    valid_parameters = False
                    continue
            except:
                error = current_switch + " '" + value + "' : Pattern does not match"
                error_list.append(error)
                valid_parameters = False
                continue

        for value in current_value.split("¬"):
            if value not in accepted_parameters[current_switch]:
                accepted_parameters[current_switch].append(value)


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
                error = switch + " (" + parameters[switch]["description"] + ") is required unless " + listtostring(parameters[switch]["required_unless"], 'or') + " is specified"
            else:
                error = switch + " (" + parameters[switch]["description"] + ") is required"
            error_list.append(error)

    for switch in parameters:
        if parameters[switch]["depends"]:
            dependency_found = True
            for dependency in parameters[switch]["depends"]:
                if dependency not in accepted_parameters:
                    dependency_found = False
                found_dependencies = dependency_found
        else:
            found_dependencies = True

        if not found_dependencies:
                valid_parameters = False
                error = switch + " (" + parameters[switch]["description"] + ") depends on " + listtostring(parameters[switch]["depends"], 'and') + " also being specified"
                error_list.append(error)

    return accepted_parameters, valid_parameters, error_list
