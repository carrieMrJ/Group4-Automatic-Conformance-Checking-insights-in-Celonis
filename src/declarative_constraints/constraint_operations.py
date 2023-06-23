from collections import defaultdict

import automata

from src.celonis_data_integration import get_connection, get_celonis_info
from src.declarative_constraints.templates import startWith, endWith, never, atMostOnce, atLeastOnce, precedence, \
    alternate_precedence, \
    chain_precedence, responded_existence, response, alternate_response, chain_response, succession, \
    alternate_succession, chain_succession, not_coexistence, not_chain_succession, not_succession
from itertools import product
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from src.get_data import mapping_traces

CONSTRAINT_LIBRARY = {"startWith": startWith, "endWith": endWith, "atMostOnce": atMostOnce, "atLeastOnce": atLeastOnce,
                      "never": never,
                      "precedence": precedence, "alternate_precedence": alternate_precedence,
                      "chain_precedence": chain_precedence, "responded_existence": responded_existence,
                      "response": response, "alternate_response": alternate_response, "chain_response": chain_response,
                      "succession": succession,
                      "alternate_succession": alternate_succession, "chain_succession": chain_succession,
                      "not_coexistence": not_coexistence,
                      "not_succession": not_succession, "not_chain_succession": not_chain_succession}


def regex_dfa(regex):
    return DFA.from_nfa(NFA.from_regex(regex))


# generate all possible constraint templates
def constraints_generation(input_symbols, constraint_names, constraint_library):
    """
    Generate all possible constraints templates with given parameters
    :param constraint_library:
    :param input_symbols: all the input modified_input_symbols
    :param constraint_names: Considered constraints templates
    :return: dictionary with key-->constraint template; value-->regular expression
    """
    # combinations of 2 parameters
    combination2 = [(x, y) for x, y in product(input_symbols, repeat=2) if x != y]
    # print("possible parameters combination:", combination2)

    constraint_regex = defaultdict(list)
    for name in constraint_names:
        template = constraint_library[name]
        # 2 parameters: input modified_input_symbols, act1
        if template.__code__.co_argcount == 2:
            for act in input_symbols:

                constraint_regex[f"{name}"].append({"parameters": act,
                                                    "regex": template(input_symbols, act)})
                if act == 'a':
                    print(template(input_symbols, act))

        # 3 parameters: input modified_input_symbols, act1, act2
        if template.__code__.co_argcount == 3:
            for comb in combination2:
                constraint_regex[f"{name}"].append({"parameters": (comb[0], comb[1]),
                                                    "regex": template(input_symbols, comb[0], comb[1])})
    valid = defaultdict(list)
    for name in constraint_regex:
        for items in constraint_regex[name]:
            valid[f"{name}"].append(items["parameters"])
    return valid


def event_log_constraint_extraction(main_trace_list, constraint_list, symbols, constraint_library):
    """
    Find out the diagnostics
    :param symbols:
    :param main_trace_list: list of string
    :param constraint_list: dictionary key:constraint name value:constraint parameter
    :return:
    """
    # list of dfa for constraints
    dfa4constraints = {}
    # list of invalid constraints
    valid_constraints = defaultdict(list)
    try:
        for key, value in constraint_list.items():
            # print(f"{key}:{value}")
            template = constraint_library[key]
            if template.__code__.co_argcount == 3:
                for item in value:
                    regex = template(symbols, item[0], item[1])
                    # print(f"regex: {regex}")
                    print(f"loading DFA for {key}:{item} {regex}")
                    dfa4constraints[f"{key}:{item}"] = regex_dfa(
                        regex)
            else:
                for item in value:
                    regex = template(symbols, item)
                    print(f"loading DFA for {key}:{item} {regex}")
                    dfa4constraints[f"{key}:{item}"] = regex_dfa(regex)
    except KeyError:
        pass
    res = defaultdict(list)
    for trace in main_trace_list:
        print(trace)
        for key, dfa in dfa4constraints.items():
            constraint_name = key.split("(")[0]
            flag = dfa.accepts_input(trace)
            if flag:
                res[f"{constraint_name}"].append(constraint_name[1])
                valid_constraints[key].append(trace)
    satisfied_constraints=list(valid_constraints.keys())
    return satisfied_constraints


# if __name__ == "__main__":
#     celonis = get_connection()
#     print(celonis)
#     # get the data pool and data model of our project
#     # print(get_celonis_info(celonis))
#     data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name, lifecycle_column_name = get_celonis_info(celonis=celonis)
#     # check if one table is invalid (does not exist in our data pool/model)
#     t, m, a = mapping_traces(data_model, "receipt", act_column_name)
#     print(t)
#     # print(a)
#     constraints_list = constraints_generation(a, CONSTRAINT_LIBRARY)
#     # constraints_list = {'C2': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A']}
#     # print(constraints_list)
#     valid_constraint = event_log_constraint_extraction(t, constraints_list, a)
#     print(valid_constraint)
#     # print(startWith(a, 'a'))