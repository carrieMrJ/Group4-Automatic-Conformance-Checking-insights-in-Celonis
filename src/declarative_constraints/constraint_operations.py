import re
from collections import defaultdict, Counter
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


def encode_trace(trace, mapping):
    encoded = ""
    tmp = trace.split(", ")
    for act in tmp:
        encoded += mapping[act]
    return encoded


# generate all possible constraint templates
def constraints_generation(encoded_input_symbols, constraint_names, constraint_library):
    """
    Generate all possible constraints templates with given parameters
    :param constraint_library:
    :param encoded_input_symbols: all the input modified_input_symbols
    :param constraint_names: Considered constraints templates
    :return: dictionary with key-->constraint template; value-->parameters
    """
    # combinations of 2 parameters
    combination2 = [(x, y) for x, y in product(encoded_input_symbols, repeat=2) if x != y]

    constraint_regex = defaultdict(list)
    for name in constraint_names:
        template = constraint_library[name]
        # 2 parameters: input act1
        if template.__code__.co_argcount == 1:
            for act in encoded_input_symbols:

                constraint_regex[f"{name}"].append({"parameters": act,
                                                    "regex": template(act)})

        # 3 parameters: input act1, act2
        if template.__code__.co_argcount == 2:
            for comb in combination2:
                constraint_regex[f"{name}"].append({"parameters": (comb[0], comb[1]),
                                                    "regex": template(comb[0], comb[1])})
    constraint_list = defaultdict(list)
    for name in constraint_regex:
        for items in constraint_regex[name]:
            constraint_list[f"{name}"].append(items["parameters"])
    return constraint_list


def event_log_constraint_extraction(trace_list, constraint_list, constraint_library, percentage_of_instances,
                                    mapping=None, reverse_mapping=None):
    """
    Find out the diagnostics
    :param mapping: encode trace
    :param reverse_mapping: decode trace
    :param percentage_of_instances: specify that a DECLARE constraint can still be discovered even if it does not hold for all process instances of the log
    :param constraint_library: all constraints
    :param trace_list:
    :param constraint_list: dictionary key:constraint name value:constraint parameter
    :return:
    """
    # list of regex for constraints
    regex4constraints = {}
    # list of invalid constraints
    try:
        for key, value in constraint_list.items():
            template = constraint_library[key]
            if template.__code__.co_argcount == 2:
                for item in value:
                    regex4constraints[f"{key}:{item[0]},{item[1]}"] = template(item[0], item[1])
            else:
                for item in value:
                    regex4constraints[f"{key}:{item}"] = template(item)
    except KeyError:
        pass
    res_ = []
    sum_case = sum(trace_list["case_count"])
    cnt = Counter()

    for idx, rows in trace_list.iterrows():
        encoded_trace = encode_trace(rows["activity_trace"], mapping)
        for key, regex in regex4constraints.items():
            flag = re.fullmatch(regex, encoded_trace)
            if flag and flag.group() != '':
                cnt[key] += rows["case_count"]
    for key, value in cnt.items():
        split = key.split(":")
        if value >= sum_case * percentage_of_instances:
            constraint_name = split[0]
            if len(split[1]) == 1:
                res_.append(f"{constraint_name}:{reverse_mapping[split[1]]}")
            else:
                params = split[1].split(",")
                res_.append(f"{constraint_name}:{reverse_mapping[params[0]]}, {reverse_mapping[params[1]]}")
    return res_
