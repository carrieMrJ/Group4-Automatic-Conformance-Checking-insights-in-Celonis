import unittest
import pandas as pd
from src.get_data import split_df

class TemporalProfileTestCase(unittest.TestCase):
    def test_split_df(self):
        example = pd.DataFrame({
            "activity_trace": ["A", "B", "C", "D", "E", "F", "G", "H"],
        })

        # Test the function with p = 0.2
        first_p, rest = split_df(example, p=0.2)

        # Assert that the length of the first_p is 20% of the total rows, rounded down
        self.assertEqual(len(first_p), int(len(example) * 0.2))

        # Assert that the length of rest is the remaining rows
        self.assertEqual(len(rest), len(example) - len(first_p))

        # Assert that the values in first_p are correct
        self.assertListEqual(first_p, [["A"]])

        # Assert that the values in rest are correct
        self.assertListEqual(rest, [["B"], ["C"], ["D"], ["E"], ["F"], ["G"], ["H"]])

if __name__ == "__main__":
    unittest.main()
