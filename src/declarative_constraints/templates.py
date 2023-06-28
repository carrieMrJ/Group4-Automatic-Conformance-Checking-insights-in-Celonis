"""
Constraints Templates
"""
# start with one specific activity
def startWith(input_symbols, act1):
    return f'^{act1}'

# end with one specific activity
def endWith(input_symbols, act1):
    return f"{act1}$"


# one activity occurs at most once
def atMostOnce(input_symbols, act1):
    return f"^[^{act1}]*{act1}?[^{act1}]*$"


# existence: act1 happens at least once
def atLeastOnce(input_symbols, act1):
    return f"^.*{act1}.*$"


# one activity never occurs
def never(input_symbols, act1):
    return f"^(?!.*{act1}).*"


# act2 is always preceded by act1
def precedence(input_symbols, act1, act2):
    return f"[^{act2}]*{act1}.*{act2}.*"


# alternate precedence: each time act2 occurs, it is preceded by act1 and no other act2 can occur in between
def alternate_precedence(input_symbols, act1, act2):
    return f"[^{act2}]*({act1}(?!{act2})*)*"


# chain precedence: each time act2 occurs, then act1 occurs immediately beforehand
def chain_precedence(input_symbols, act1, act2):
    return f"[^{act2}]*({act1}{act2})*[^{act2}]*"


# responded existence: if act1 occurs, then act2 occurs as well
def responded_existence(input_symbols, act1, act2):
    return f"[^{act1}]*({act1}[^{act2}]*{act2}.*)?"


# response: if act1 occurs then act2 occurs after act1
def response(input_symbols, act1, act2):
    return f"[^{act1}]*({act1}{act2})*[^{act1}]*"


# alternate response: each time act1 occurs then act2 occurs afterwards, and no other act1 occurs in between
def alternate_response(input_symbols, act1, act2):
    return f"[^{act1}]*(({act1}[^{act1}{act2}]*{act2}[^{act1}]*)+)?"


# chain response: each time allow_act1 occurs then allow_act2 occurs immediately after
def chain_response(input_symbols, act1, act2):
    return f"[^{act1}]*(({act1}{act2}[^{act1}]*)+)?"


# succession: allow_act1 occurs if only if it is followed by allow_act2
def succession(input_symbols, act1, act2):
    return f"[^{act1}]*({act1}[^{act2}]*{act2}[^{act1}]*)*"


# alternate succession: act1 and act2 iff the latter follows the former and they alternate each other in the act
def alternate_succession(input_symbols, act1, act2):
    return f"[^{act1}{act2}]*({act1}([^{act1}{act2}])*{act2})*([^{act1}{act2}])*"


# chain succession: allow_act1 and allow_act2 iff the latter immediately follow the former
def chain_succession(input_symbols, act1, act2):
    return f"[^{act1}]*({act1}{act2}[^{act1}{act2}]*)*"


# not co-existence: allow_act1 and allow_act2 cannot occur within one act
def not_coexistence(input_symbols, act1, act2):
    return f"[^{act1}{act2}]*({act1}[^{act2}]*|{act2}[^{act1}]*)?"


# not succession: allow_act2 cannot occur after allow_act1
def not_succession(input_symbols, act1, act2):
    return f"[^{act1}]*{act1}[^{act2}]*"


# not chain succession: act1 and act2 can not occur contiguously
def not_chain_succession(input_symbols, act1, act2):
    return f"[^{act1}]*({act1}+[^{act1}{act2}][^{act1}]*)*({act1}+)?"



