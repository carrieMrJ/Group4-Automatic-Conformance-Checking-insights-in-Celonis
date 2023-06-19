import unittest
from itertools import product
from collections import defaultdict

from src.declarative_constraints.constraint_operations import event_log_constraint_extraction, constraints_generation

# Define CONSTRAINT_LIBRARY
CONSTRAINT_LIBRARY = {
    'constraint1': lambda input_symbols, act1: f"{act1}*",
    'constraint2': lambda input_symbols, act1, act2: f"({act1}|{act2})*"
}


# Define the unit tests
class TestConstraints(unittest.TestCase):
    def test_constraints_generation(self):
        input_symbols = ['a', 'b', 'c']
        constraint_names = ['constraint1', 'constraint2']
        expected_result = {
            'constraint1': ['a', 'b', 'c'],
            'constraint2': [('a', 'b'), ('a', 'c'), ('b', 'a'), ('b', 'c'), ('c', 'a'), ('c', 'b')]
        }
        result = constraints_generation(input_symbols, constraint_names, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)

    def test_constraints_generation_empty_input_symbols(self):
        input_symbols = []
        constraint_names = ['constraint1', 'constraint2']
        expected_result = {}
        result = constraints_generation(input_symbols, constraint_names, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)

    def test_constraints_generation_empty_constraint_names(self):
        input_symbols = ['a', 'b', 'c']
        constraint_names = []
        expected_result = {}
        result = constraints_generation(input_symbols, constraint_names, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)

    def test_constraints_generation_duplicate_parameters(self):
        input_symbols = ['a', 'b', 'a']
        constraint_names = ['constraint1', 'constraint2']
        expected_result = {
            'constraint1': ['a', 'b', 'a'],
            'constraint2': [('a', 'b'), ('b', 'a'), ('b', 'a'), ('a', 'b')]
        }
        result = constraints_generation(input_symbols, constraint_names, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction(self):
        main_trace_list = ['aaa', 'bbb', 'abab', "cdcd"]
        constraint_list = {
            'constraint1': ['a', 'b'],
            'constraint2': [['a', 'b'], ['c', 'd']]
        }
        symbols = ['a', 'b', 'c', 'd']
        expected_result = {
            'constraint1:a': ['aaa'],
            'constraint1:b': ['bbb'],
            'constraint2:[\'a\', \'b\']': ['aaa', 'bbb', 'abab'],
            'constraint2:[\'c\', \'d\']': ['cdcd']
        }
        result = event_log_constraint_extraction(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction_empty_main_trace_list(self):
        main_trace_list = []
        constraint_list = {
            'constraint1': ['a', 'b'],
            'constraint2': [['a', 'b'], ['c', 'd']]
        }
        symbols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        expected_result = {}
        result = event_log_constraint_extraction(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction_empty_constraint_list(self):
        main_trace_list = ['abc', 'def', 'ghi']
        constraint_list = {}
        symbols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        expected_result = {}
        result = event_log_constraint_extraction(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction_constraints_with_different_arities(self):
        main_trace_list = ['aaa', 'bbb', 'abab', 'cdcd']
        constraint_list = {
            'constraint1': ['a', 'b'],
            'constraint2': [['a', 'b'], ['c', 'd']],
            'constraint3': [['a', 'b', 'c']]
        }
        symbols = ['a', 'b', 'c', 'd']
        expected_result = {
            'constraint1:a': ['aaa'],
            'constraint1:b': ['bbb'],
            'constraint2:[\'a\', \'b\']': ['aaa', 'bbb', 'abab'],
            'constraint2:[\'c\', \'d\']': ['cdcd']
        }
        result = event_log_constraint_extraction(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction_traces_not_matching_constraints(self):
        main_trace_list = ['abc', 'def', 'ghi']
        constraint_list = {
            'constraint1': ['x', 'y'],
            'constraint2': [['m', 'n']],
        }
        symbols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        expected_result = {}
        result = event_log_constraint_extraction(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
