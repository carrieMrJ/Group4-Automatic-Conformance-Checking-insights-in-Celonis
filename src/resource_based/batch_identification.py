import pandas as pd
import warnings
from src.data_integration.get_data import get_res_act_relation


def batch_identification(df, activities):
    """
    Identify all possible batches for al available combination of resources and activities
    :param df: data frame with case_id, activity, resource, start_at, end_at
    :param activities: list of all kinds of activities in df
    :return: 3 batches
    """

    warnings.filterwarnings('ignore')
    res_act_dict = get_res_act_relation(df, activities)
    group_res_act = df.groupby(["resource", "activity"])

    sim = []
    seq = []
    con = []
    invalid = []

    for a in activities:
        for r in res_act_dict[a]:

            data_res_act = group_res_act.get_group((r, a))
            data_res_act["start_at"] = data_res_act["start_at"].round("T")
            data_res_act["end_at"] = data_res_act["end_at"].round("T")
            data_res_act = data_res_act.sort_values(by=["start_at", "end_at"])

            data = data_res_act.values

            for row1 in data:
                for row2 in data:
                    if sum(row1 != row2) == 0:
                        continue
                    if (row1[3] == row2[3]) and (row1[4] == row2[4]):
                        sim.append(row1[2])
                    elif (row1[3] == row2[4]) or (row1[4] == row2[3]):
                        seq.append(row1[2])
                    elif (row1[4] < row2[3]) or (row2[4] < row1[3]):
                        invalid.append(row1[2])
                    else:
                        con.append(row2[2])
    df_sim = pd.DataFrame(sim,
                          columns=["Simultaneous"]).drop_duplicates()
    df_seq = pd.DataFrame(seq,
                          columns=["Sequential"]).drop_duplicates()
    df_con = pd.DataFrame(con,
                          columns=["Concurrent"]).drop_duplicates()

    return df_sim, df_seq, df_con
