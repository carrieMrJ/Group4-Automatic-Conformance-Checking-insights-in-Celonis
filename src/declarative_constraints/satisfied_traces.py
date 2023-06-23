from constraint_operations import CONSTRAINT_LIBRARY,regex_dfa



def get_satisfied_constraints(main_trace_list, constraint_list, symbols, constraint_library):
    """
    Find out the diagnostics
    :param symbols:
    :param main_trace_list: list of string
    :param constraint_list: dictionary key:constraint name value:constraint parameter
    :return: list of satisfied constraints by the mainstream traces
    """
    # list of dfa for constraints
    dfa4constraints = {}
    # list of valid constraints
    valid_constraints = defaultdict(list)
    try:
        for key, value in constraint_list.items():
            template = constraint_library[key]
            if template.__code__.co_argcount == 3:
                for item in value:
                    regex = template(symbols, item[0], item[1])
                    dfa4constraints[f"{key}:{item}"] = regex_dfa(regex)
            else:
                for item in value:
                    regex = template(symbols, item)
                    dfa4constraints[f"{key}:{item}"] = regex_dfa(regex)
    except KeyError:
        pass
    for trace in main_trace_list:
        for key, dfa in dfa4constraints.items():
            constraint_name = key.split("(")[0]
            flag = dfa.accepts_input(trace)
            if flag:
                valid_constraints[constraint_name].append(trace)
    satisfied_constraints=list(valid_constraints.keys())
    return satisfied_constraints

import re

def find_anomalies(new_observation_traces, satisfied_constraints, symbols, CONSTRAINT_LIBRARY):
    """
    Find anomalies in new observation traces based on satisfied constraints
    :param new_observation_traces: list of strings (new observation traces)
    :param satisfied_constraints: list of satisfied constraints
    :param symbols: list of symbols
    :param CONSTRAINT_LIBRARY: dictionary of constraint templates
    :return: list of anomalies (traces that do not satisfy the constraints)
    """
    anomalies = []

    for trace in new_observation_traces:
        trace_satisfies_constraints = False

        for constraint in satisfied_constraints:
            constraint_name, *constraint_params = constraint.split(":")
            template = CONSTRAINT_LIBRARY[constraint_name]

            if template.__code__.co_argcount == 3:
                for params in constraint_params:
                    regex = template(symbols, *params)
                    if re.match(regex, trace):
                        trace_satisfies_constraints = True
                        break
            else:
                regex = template(symbols, *constraint_params)
                if re.match(regex, trace):
                    trace_satisfies_constraints = True
                    break

        if not trace_satisfies_constraints:
            anomalies.append(trace)

    return anomalies
