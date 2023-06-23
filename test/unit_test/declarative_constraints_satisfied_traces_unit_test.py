import unittest
from src.declarative_constraints.satisfied_traces import get_satisfied_constraints,find_anomalies


import re
import unittest

CONSTRAINT_LIBRARY = {
    "startWith": lambda symbols, prefix: f"^{re.escape(prefix)}",
    "endWith": lambda symbols, suffix: f"{re.escape(suffix)}$",
    "atMostOnce": lambda symbols, char: f"(?=.*{re.escape(char)})"
}


class TestGetSatisfiedConstraints(unittest.TestCase):
    def test_get_satisfied_constraints(self):
        main_trace_list = ["abc", "def", "ghi"]
        constraint_list = {
            "startWith": ["abc"],
            "endWith": ["cba"],
            "atMostOnce": ["abc"]
        }
        symbols = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A"]

        expected_result = ["startWith", "atMostOnce"]

        # Call the function
        result = get_satisfied_constraints(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)

        self.assertEqual(result, expected_result)

    def test_get_satisfied_constraints_empty_trace_list(self):
        main_trace_list = []
        constraint_list = {
            "startWith": ["abc"],
            "endWith": ["cba"],
            "atMostOnce": ["abc"]
        }
        symbols = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A"]

        expected_result = []

        # Call the function
        result = get_satisfied_constraints(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)

        self.assertEqual(result, expected_result)

    def test_get_satisfied_constraints_empty_constraint_list(self):
        main_trace_list = ["abc", "def", "ghi"]
        constraint_list = {}
        symbols = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A"]

        expected_result = []

        # Call the function
        result = get_satisfied_constraints(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)

        self.assertEqual(result, expected_result)

    def test_get_satisfied_constraints_custom_constraint(self):
        main_trace_list = ["abc", "def", "ghi"]
        constraint_list = {
            "customConstraint": ["abc"]
        }
        symbols = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A"]
        CONSTRAINT_LIBRARY["customConstraint"] = lambda symbols, prefix: f"^{re.escape(prefix)}"

        expected_result = ["customConstraint"]

        # Call the function
        result = get_satisfied_constraints(main_trace_list, constraint_list, symbols, CONSTRAINT_LIBRARY)

        self.assertEqual(result, expected_result)

    def test_find_anomalies(self):
        new_observation_traces = ["abc", "def", "xyz"]
        satisfied_constraints = ["startWith:abc", "atMostOnce:abc"]
        symbols = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

        expected_result = ["def", "xyz"]

        # Call the function
        result = find_anomalies(new_observation_traces, satisfied_constraints, symbols, CONSTRAINT_LIBRARY)

        self.assertEqual(result, expected_result)

    def test_find_anomalies_empty_traces(self):
        new_observation_traces = []
        satisfied_constraints = ["startWith:abc", "atMostOnce:abc"]
        symbols = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

        expected_result = []

        # Call the function
        result = find_anomalies(new_observation_traces, satisfied_constraints, symbols, CONSTRAINT_LIBRARY)

        self.assertEqual(result, expected_result)

    def test_find_anomalies_empty_constraints(self):
        new_observation_traces = ["abc", "def", "xyz"]
        satisfied_constraints = []
        symbols = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

        expected_result = ["abc", "def", "xyz"]

        # Call the function
        result = find_anomalies(new_observation_traces, satisfied_constraints, symbols, CONSTRAINT_LIBRARY)

        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()

        