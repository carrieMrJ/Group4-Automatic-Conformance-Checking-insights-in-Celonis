import unittest
import pandas as pd
from unittest.mock import patch
from io import StringIO
from src.data_integration.get_data import get_unique_activity, get_unique_resource
from src.resource_based.batch_identification import batch_identification
from src.resource_based.find_high_rework_resources_analysis import find_high_rework_resources
from src.resource_based.find_deviations_analysis import find_deviations

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

        df_sim, df_seq, df_con = batch_identification(example, get_unique_activity(example, "activity"))
        df_sim_expected = pd.DataFrame(['X', 'Y'], columns=['Simultaneous'])
        df_seq_expected = pd.DataFrame(['X', 'Y'], columns=['Sequential'])
        df_con_expected = pd.DataFrame(['X'], columns=['Concurrent'])
        
        pd.testing.assert_frame_equal(df_sim.reset_index(drop=True), df_sim_expected.reset_index(drop=True))
        pd.testing.assert_frame_equal(df_seq.reset_index(drop=True), df_seq_expected.reset_index(drop=True))
        pd.testing.assert_frame_equal(df_con.reset_index(drop=True), df_con_expected.reset_index(drop=True))


    def test_find_deviations(self):
        example = pd.DataFrame({
        'case_id': ['case1', 'case1', 'case1', 'case2', 'case2', 'case2', 'case3', 'case3', 'case3', 'case4', 'case4', 'case4'],
        'activity': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'D'],
        'resource': ['res1', 'res1', 'res1', 'res2', 'res2', 'res2', 'res3', 'res3', 'res3', 'res1', 'res1', 'res1']
        })
        
        expected_output = pd.DataFrame({
        "resource": ['res1', 'res2', 'res2', 'res2', 'res3', 'res3', 'res3', 'res1'],
        "unusual_activity": ['C', 'A', 'B', 'C', 'A', 'B', 'C', 'D'],
        "case": ['case1', 'case2', 'case2', 'case2', 'case3', 'case3', 'case3', 'case4']
        })
        
        real_output = find_deviations(example, 1)
        pd.testing.assert_frame_equal(real_output, expected_output)
        

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
