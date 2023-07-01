import unittest
import pandas as pd
from src.get_data import split_df
from src.temporal_profile.calculate_score import get_z_score

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

    def test_get_z_score(self):
        raw_dur={'case_id':['t1'],
            'start_activity':['A'],
            'end_activity':['A'],
            'start_life':['x'],
            'end_life':['x'],
            'task_duration(min)':[19]
        }
        df_dur=pd.DataFrame(raw_dur)

        raw_dis={'case_id':['t1'],
            'start_activity':['A'],
            'end_activity':['B'],
            'start_life':['x'],
            'end_life':['x'],
            'start_timestamp':[19],
            'end_timestamp':[29],
            'time_distance(min)':[10]
        }
        df_dis=pd.DataFrame(raw_dis)

        raw_tdur={'Activity':['A'],
            'max_task_duration(min)':[500],
            'min_task_duration(min)':[0],
            'mean_task_duration(min)':[20],
            'stdev_task_duration(min)':[4],
            'var_task_duration(min)':[16]
        }
        df_tdur=pd.DataFrame(raw_tdur)

        raw_tdis={'Start_activity':['A'],
                  'End_activity':['B'],
            'max_time_distance(min)':[500],
            'min_time_distance(min)':[0],
            'mean_time_distance(min)':[3],
            'stdev_time_distance(min)':[0.5],
            'var_time_distance':[0.25]
        }
        df_tdis=pd.DataFrame(raw_tdis)

        ndur, adur, ndis, adis = get_z_score(df_dur, df_dis, df_tdur, df_tdis, 3)

        #Assert the list of the normal-task-duration
        self.assertListEqual(ndur[0].tolist(), ['t1', 'A', 'A', 'x', 'x', 19])

        #Assert the length of the anomaly-task-duration
        self.assertEqual(len(adur), 0)

        #Assert the length of the normal-time-distance
        self.assertEqual(len(ndis), 0)

        #Assert the list of the anomaly-time-distance
        self.assertListEqual(adis[0].tolist(), ['t1', 'A', 'B', 'x', 'x', 19, 29, 10])

if __name__ == "__main__":
    unittest.main()
