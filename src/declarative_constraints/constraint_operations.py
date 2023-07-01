import re
from collections import defaultdict
from src.declarative_constraints.templates import startWith, endWith, never, atMostOnce, atLeastOnce, precedence, \
    alternate_precedence, \
    chain_precedence, responded_existence, response, alternate_response, chain_response, succession, \
    alternate_succession, chain_succession, not_coexistence, not_chain_succession, not_succession
from itertools import product

CONSTRAINT_LIBRARY = {"startWith": startWith, "endWith": endWith, "atMostOnce": atMostOnce, "atLeastOnce": atLeastOnce,
                      "never": never,
                      "precedence": precedence, "alternate_precedence": alternate_precedence,
                      "chain_precedence": chain_precedence, "responded_existence": responded_existence,
                      "response": response, "alternate_response": alternate_response, "chain_response": chain_response,
                      "succession": succession,
                      "alternate_succession": alternate_succession, "chain_succession": chain_succession,
                      "not_coexistence": not_coexistence,
                      "not_succession": not_succession, "not_chain_succession": not_chain_succession}


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
    :param constraint_library:
    :param symbols:
    :param main_trace_list: list of string
    :param constraint_list: dictionary key:constraint name value:constraint parameter
    :return:
    """
    # list of dfa for constraints
    regex4constraints = {}
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
                    print(f"loading regex for {key}:{item} {regex}")
                    # dfa4constraints[f"{key}:{item}"] = regex_dfa(
                    #     regex)
                    regex4constraints[f"{key}:{item[0]},{item[1]}"] = regex
            else:
                for item in value:
                    regex = template(symbols, item)
                    print(f"loading regex for {key}:{item} {regex}")
                    # dfa4constraints[f"{key}:{item}"] = regex_dfa(regex)
                    regex4constraints[f"{key}:{item}"] = regex
    except KeyError:
        pass
    # res = defaultdict(set)
    res_ = {}
    for trace in main_trace_list:
        print(trace)
        tmp = defaultdict(set)
        for key, regex in regex4constraints.items():
            constraint_name = key.split(":")
            # flag = dfa.accepts_input(trace)
            flag = re.fullmatch(regex, trace)
            print(f"{regex}:{trace}={flag}")
            if flag and flag.group() != '':
                tmp[f"{constraint_name[0]}"].add(constraint_name[1])
                # res[f"{constraint_name[0]}"].add(constraint_name[1])
                valid_constraints[key].append(trace)
        res_[trace] = tmp
    # satisfied_constraints = list(valid_constraints.keys())
    return res_
