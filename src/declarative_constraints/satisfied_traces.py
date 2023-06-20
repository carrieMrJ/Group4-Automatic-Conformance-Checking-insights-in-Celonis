from constraint_operations import CONSTRAINT_LIBRARY,regex_dfa



def get_satisfied_constraints(main_trace_list, constraint_list, symbols, constraint_library):
    """
    Get the list of constraints satisfied by the mainstream traces
    :param main_trace_list: List of strings representing the mainstream traces
    :param constraint_list: Dictionary with constraint names as keys and constraint parameters as values
    :param symbols: List of input symbols
    :param CONSTRAINT_LIBRARY: Dictionary with constraint names as keys and constraint functions as values
    :return: List of constraint names satisfied by the mainstream traces
    """
    # List of DFAs for constraints
    dfa4constraints = {}

    for key, value in constraint_list.items():
        x = constraint_library.get(key)

        if x is None:
            continue

        if x.__code__.co_argcount == 3:
            for item in value:
                regex = x(symbols, item[0], item[1])
                dfa4constraints[f"{key}:{item}"] = regex_dfa(regex)
        else:
            for item in value:
                regex = x(symbols, item)
                dfa4constraints[f"{key}:{item}"] = regex_dfa(regex)

    satisfied_constraints = []

    for trace in main_trace_list:
        for key, dfa in dfa4constraints.items():
            constraint_name = key.split("(")[0]
            if dfa.accepts_input(trace):
                satisfied_constraints.append(constraint_name)
                break

    return satisfied_constraints


def find_anomalies(new_observation_traces, satisfied_constraints, symbols, constraint_library):
    """
    Find anomalies in the observation traces based on the satisfied constraints
    :param new_observation_traces: List of strings representing the observation traces
    :param satisfied_constraints: List of constraints satisfied by the mainstream traces
    :param symbols: List of input symbols
    :param constraint_library: Dictionary with constraint names as keys and constraint functions as values
    :return: List of anomaly traces (new observation traces that dont satisfy the constraints which were satisfied by mainstream cases)
    """
    anomaly_traces = []

    for trace in new_observation_traces:
        for constraint_name in satisfied_constraints:
            template = constraint_library.get(constraint_name)
            if template is not None:
                if template.__code__.co_argcount == 3:
                    for symbol1 in symbols:
                        for symbol2 in symbols:
                            if symbol1 != symbol2 and not template(symbols, symbol1, symbol2).accepts_input(trace):
                                anomaly_traces.append(trace)
                                break
                else:
                    for symbol in symbols:
                        if not template(symbols, symbol).accepts_input(trace):
                            anomaly_traces.append(trace)
                            break

    return anomaly_traces
