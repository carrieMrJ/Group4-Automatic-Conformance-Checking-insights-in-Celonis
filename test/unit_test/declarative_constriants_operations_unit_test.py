import unittest
from itertools import product
from collections import defaultdict

import pandas as pd

from src.declarative_constraints.constraint_operations import event_log_constraint_extraction, constraints_generation

# Define CONSTRAINT_LIBRARY
CONSTRAINT_LIBRARY = {
    'constraint1': lambda act1: f"{act1}*",
    'constraint2': lambda act1, act2: f"({act1}|{act2})*"
}


# Define the unit tests
class TestConstraints(unittest.TestCase):
    def test_constraints_generation(self):
        input_symbols = ['a', 'b', 'c']
        constraint_names = ['constraint1', 'constraint2']
        expected_result = {'constraint1': ['a', 'b', 'c'],
                           'constraint2': [('a', 'b'),
                                           ('a', 'c'),
                                           ('b', 'a'),
                                           ('b', 'c'),
                                           ('c', 'a'),
                                           ('c', 'b')]}
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
        trace_list = pd.DataFrame({
            "case_count": [40, 20, 10],
            "activity_trace": ['a, b, c', 'x, y, z', 'y, a, z']
        })
        constraint_list = {
            'constraint1': [['1', '3'], ['8', '9']],
            'constraint2': ['7', '8', '9']

        }
        constraint_library = {
            'constraint1': lambda param1, param2: f"{param1}.*{param2}",
            'constraint2': lambda param: f"^{param}.*$"
        }
        percentage_of_instances = 0.2
        mapping = {'a': "1", 'b': "2", 'c': "3", 'd': "4", "x": "7", "y": "8", "z": "9"}
        reverse_mapping = {v: k for k, v in mapping.items()}
        expected_result = ['constraint1:a, c', 'constraint2:x']
        result = event_log_constraint_extraction(trace_list, constraint_list, constraint_library,
                                                 percentage_of_instances, mapping, reverse_mapping)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction_empty_trace_list(self):
        trace_list = pd.DataFrame({
            "case_count": [],
            "activity_trace": []
        })
        constraint_list = {
            'constraint1': [['1', '2'], ['3', '4']],
            'constraint2': ['7', '8', '9']

        }
        constraint_library = {
            'constraint1': lambda param1, param2: f"{param1}.*{param2}",
            'constraint2': lambda param: f"^{param}.*$"
        }
        percentage_of_instances = 0.5
        mapping = {'a': "1", 'b': "2", 'c': "3", 'd': "4", "x": "7", "y": "8", "z": "9"}
        reverse_mapping = {v: k for k, v in mapping.items()}
        expected_result = []
        result = event_log_constraint_extraction(trace_list, constraint_list, constraint_library,
                                                 percentage_of_instances, mapping, reverse_mapping)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction_empty_constraint_list(self):
        trace_list = pd.DataFrame({
            "case_count": [40, 20, 10],
            "activity_trace": ['a, b, c', 'd, e, f', 'g, h, i']
        })
        constraint_list = {}
        constraint_library = CONSTRAINT_LIBRARY
        percentage_of_instances = 0.5
        mapping = {'a': "1", 'b': "2", 'c': "3", 'd': "4", "e": "5", "f": "6", "g": "7", "h": "8", "i": "9"}
        reverse_mapping = {v: k for k, v in mapping.items()}
        expected_result = []
        result = event_log_constraint_extraction(trace_list, constraint_list, constraint_library,
                                                 percentage_of_instances, mapping, reverse_mapping)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction_no_matching_constraints(self):
        trace_list = pd.DataFrame({
            "case_count": [40, 20, 10],
            "activity_trace": ['a, b, c', 'd, e, f', 'g, h, i']
        })
        constraint_list = {
            'constraint2': ['2', '5'],
            'constraint1': [['3', '6']],
        }
        constraint_library = {
            'constraint1': lambda param1, param2: f"{param1}.*{param2}",
            'constraint2': lambda param: f"^{param}.*$"
        }
        percentage_of_instances = 0.5
        mapping = {'a': "1", 'b': "2", 'c': "3", 'd': "4", "e": "5", "f": "6", "g": "7", "h": "8", "i": "9"}
        reverse_mapping = {v: k for k, v in mapping.items()}
        expected_result = []
        result = event_log_constraint_extraction(trace_list, constraint_list, constraint_library,
                                                 percentage_of_instances, mapping, reverse_mapping)
        self.assertEqual(result, expected_result)

    def test_event_log_constraint_extraction_matching_multiple_constraints(self):
        trace_list = pd.DataFrame({
            "case_count": [40, 20, 10],
            "activity_trace": ['a, b, c', 'd, e, f', 'g, h, i']
        })
        constraint_list = {
            'constraint1': [['1', '3'], ['3', '4']],
            'constraint2': ['1', '2'],
        }
        constraint_library = {
            'constraint1': lambda param1, param2: f"{param1}.*{param2}",
            'constraint2': lambda param: f"^{param}.*$"
        }

        percentage_of_instances = 0.5
        mapping = {'a': "1", 'b': "2", 'c': "3", 'd': "4", "e": "5", "f": "6", "g": "7", "h": "8", "i": "9"}
        reverse_mapping = {v: k for k, v in mapping.items()}
        expected_result = ['constraint1:a, c', 'constraint2:a']
        result = event_log_constraint_extraction(trace_list, constraint_list, constraint_library,
                                                 percentage_of_instances, mapping, reverse_mapping)
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
