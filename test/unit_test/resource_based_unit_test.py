import unittest
import pandas as pd
from unittest.mock import patch
from io import StringIO
from src.get_data import get_unique_activity, get_unique_resource
from src.resource_based_analysis import batch_identification
from src.retrieve_data_for_activities_repeated_by_difference_resources_PQL import get_caseid_activity_lifecycle_resource
from src.find_high_rework_resources_analysis import find_high_rework_resources
from src.find_deviations_analysis import find_deviations

class ResourceBasedTestCase(unittest.TestCase):
    def test_unique_activity_resource(self):
        example = pd.DataFrame({
            "case_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "activity": ["A", "B", "A", "B", "A", "B", "A", "B"],
            "resource": ["X", "Y", "X", "Y", "X", "Y", "X", "Y"],
            "start_at": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 09:05:00",
                                        "2023-01-01 10:00:00", "2023-01-01 09:20:00",
                                        "2023-01-01 10:10:00", "2023-01-01 11:05:00",
                                        "2023-01-01 11:00:00", "2023-01-01 11:05:00"]),
            "end_at": pd.to_datetime(["2023-01-01 10:10:00", "2023-01-01 09:20:00",
                                      "2023-01-01 10:10:00", "2023-01-01 10:20:00",
                                      "2023-01-01 11:10:00", "2023-01-01 11:20:00",
                                      "2023-01-01 11:10:00", "2023-01-01 11:20:00"])
        })
        correct_res_act = ['A', 'B']
        self.assertListEqual(list(get_unique_activity(example, "activity")), correct_res_act)
        correct_res_res = ['X', 'Y']
        self.assertListEqual(list(get_unique_resource(example, "resource")), correct_res_res)

    def test_batch_identification(self):
        example = pd.DataFrame({
            "case_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "activity": ["A", "B", "A", "B", "A", "B", "A", "B"],
            "resource": ["X", "Y", "X", "Y", "X", "Y", "X", "Y"],
            "start_at": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 09:05:00",
                                        "2023-01-01 10:00:00", "2023-01-01 09:20:00",
                                        "2023-01-01 10:10:00", "2023-01-01 11:05:00",
                                        "2023-01-01 11:00:00", "2023-01-01 11:05:00"]),
            "end_at": pd.to_datetime(["2023-01-01 10:10:00", "2023-01-01 09:20:00",
                                      "2023-01-01 10:10:00", "2023-01-01 10:20:00",
                                      "2023-01-01 11:10:00", "2023-01-01 11:20:00",
                                      "2023-01-01 11:10:00", "2023-01-01 11:20:00"])
        })

        d = batch_identification(example, get_unique_activity(example, "activity"))
        print(d)
        key1 = ('A', 'X')
        correct_sim_A_X = pd.DataFrame({"case_id": [1, 3],
                                        "activity": ["A", "A"],
                                        "resource": ["X", "X"],
                                        "start_at": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 10:00:00"]),
                                        "end_at": pd.to_datetime(["2023-01-01 10:10:00", "2023-01-01 10:10:00"])})

        for idx, rows in correct_sim_A_X.iterrows():
            self.assertIn(rows["case_id"], list(d[key1]["Simultaneous"]["case_id"]))

        correct_seq_A_X = pd.DataFrame({"case_id": [1, 3, 5],
                                        "activity": ["A", "A", "A"],
                                        "resource": ["X", "X", "X"],
                                        "start_at": pd.to_datetime(
                                            ["2023-01-01 10:00:00", "2023-01-01 10:00:00", "2023-01-01 10:10:00"]),
                                        "end_at": pd.to_datetime(
                                            ["2023-01-01 10:10:00", "2023-01-01 10:10:00", "2023-01-01 11:10:00"])})
        for idx, rows in correct_seq_A_X.iterrows():
            self.assertIn(rows["case_id"], list(d[key1]["Sequential"]["case_id"]))

        correct_con_A_X = pd.DataFrame({"case_id": [7, 5],
                                        "activity": ["A", "A"],
                                        "resource": ["X", "X"],
                                        "start_at": pd.to_datetime(["2023-01-01 11:00:00", "2023-01-01 11:10:00", ]),
                                        "end_at": pd.to_datetime(["2023-01-01 10:10:00", "2023-01-01 10:10:00"])})
        for idx, rows in correct_con_A_X.iterrows():
            self.assertIn(rows["case_id"], list(d[key1]["Concurrent"]["case_id"]))

        key2 = ('B', 'Y')
        correct_sim_B_Y = pd.DataFrame({"case_id": [6, 8],
                                        "activity": ["B", "B"],
                                        "resource": ["Y", "Y"],
                                        "start_at": pd.to_datetime(["2023-01-01 11:05:00", "2023-01-01 11:20:00", ]),
                                        "end_at": pd.to_datetime(["2023-01-01 11:05:00", "2023-01-01 11:20:00"])})
        for idx, rows in correct_sim_B_Y.iterrows():
            self.assertIn(rows["case_id"], list(d[key2]["Simultaneous"]["case_id"]))

        correct_seq_B_Y = pd.DataFrame({"case_id": [2, 4],
                                        "activity": ["B", "B"],
                                        "resource": ["Y", "Y"],
                                        "start_at": pd.to_datetime(["2023-01-01 09:05:00", "2023-01-01 09:20:00", ]),
                                        "end_at": pd.to_datetime(["2023-01-01 09:20:00", "2023-01-01 10:20:00"])})
        for idx, rows in correct_seq_B_Y.iterrows():
            self.assertIn(rows["case_id"], list(d[key2]["Sequential"]["case_id"]))

    def test_find_deviations(self):
        example = pd.DataFrame({
        'case_id': ['case1', 'case1', 'case1', 'case2', 'case2', 'case2', 'case3', 'case3', 'case3', 'case4', 'case4', 'case4'],
        'activity': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'D'],
        'resource': ['res1', 'res1', 'res1', 'res2', 'res2', 'res2', 'res3', 'res3', 'res3', 'res1', 'res1', 'res1']
        })
        with patch('sys.stdout', new=StringIO()) as fake_out:
            find_deviations(example, 1)
        self.assertIn('Deviation found: Resource res1 performed unusual activity C in case case1', fake_out.getvalue())
        

    def test_find_high_rework_resources(self):
        example = pd.DataFrame({
            "case_id": ['case1', 'case1', 'case1', 'case1', 'case1', 'case1', 'case1', 'case1', 'case1', 'case2', 'case2', 'case2', 'case2', 'case2', 'case2', 'case2', 'case2', 'case2'],
            "activity": ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
            "resource": ['res1', 'res1', 'res1', 'res1', 'res1', 'res1', 'res2', 'res2', 'res2', 'res3', 'res3', 'res3', 'res3', 'res3', 'res3', 'res4', 'res4', 'res4'],
            "transition": ['start', 'start', 'start', 'start', 'complete', 'complete', 'complete', 'complete', 'complete', 'start', 'start', 'start', 'start', 'complete', 'complete', 'complete', 'complete', 'complete'],
        })
        high_rework_resources = find_high_rework_resources(example, rework_threshold=0, count_threshold=3)
        self.assertListEqual(high_rework_resources, ['res1', 'res3'])        


if __name__ == "__main__":
    unittest.main()
