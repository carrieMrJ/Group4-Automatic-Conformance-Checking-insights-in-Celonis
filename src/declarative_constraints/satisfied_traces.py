from constraint_operations import CONSTRAINT_LIBRARY,regex_dfa



def get_satisfied_constraints(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY):
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
        template = CONSTRAINT_LIBRARY.get(key)

        if template is None:
            continue

        if template.__code__.co_argcount == 3:
            for item in value:
                regex = template(symbols, item[0], item[1])
                dfa4constraints[f"{key}:{item}"] = regex_dfa(regex)
        else:
            for item in value:
                regex = template(symbols, item)
                dfa4constraints[f"{key}:{item}"] = regex_dfa(regex)

    satisfied_constraints = []

    for trace in main_trace_list:
        for key, dfa in dfa4constraints.items():
            constraint_name = key.split("(")[0]
            if dfa.accepts_input(trace):
                satisfied_constraints.append(constraint_name)
                break

    return satisfied_constraints
