from constraint_operations import CONSTRAINT_LIBRARY,regex_dfa


import re

def find_anomalies(new_observation_traces, valid_constraints, symbols, CONSTRAINT_LIBRARY):
    """
    Find anomalies in new observation traces based on satisfied constraints
    :param new_observation_traces: list of strings (new observation traces)
    :param satisfied_constraints: list of satisfied constraints
    :param symbols: list of symbols
    :param CONSTRAINT_LIBRARY: dictionary of constraint templates
    :return: list of anomalies (traces that do not satisfy the constraints)
    """
    satisfied_constraints = list(valid_constraints.keys())
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
