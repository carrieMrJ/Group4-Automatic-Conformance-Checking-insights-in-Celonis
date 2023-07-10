from pycelonis.pql import PQLColumn, PQLFilter
from pycelonis_core.utils.errors import PyCelonisNotFoundError
from pycelonis.errors import PyCelonisDataExportFailedError
import string
from src.data_integration.celonis_data_integration import execute_PQL_query


def get_execution_time_per_res_per_act(data_mode, table_name, case_column, activity_column, resource_column,
                                       timestamp_column):
    columns = [PQLColumn(name="case_id", query=f'SOURCE("{table_name}"."{case_column}")'),
               PQLColumn(name="source_act", query=f'SOURCE("{table_name}"."{activity_column}")'),
               PQLColumn(name="source_resource", query=f'SOURCE("{table_name}"."{resource_column}")'),
               PQLColumn(name="target_act", query=f'TARGET("{table_name}"."{activity_column}")'),
               PQLColumn(name="source_timestamp", query=f'SOURCE("{table_name}"."{timestamp_column}")'),
               PQLColumn(name="target_timestamp", query=f'TARGET("{table_name}"."{timestamp_column}")'),
               PQLColumn(name="time_between",
                         query=f'minutes_between(SOURCE("{table_name}"."{timestamp_column}"), TARGET("{table_name}"."{timestamp_column}"))')]
    res = execute_PQL_query(data_mode, columns)
    return res


def get_caseid_activity_lifecycle_resource(data_model, table_name, case_column, activity_column, resource_column,
                                           lifecycle_column):
    columns = [PQLColumn(name="case_id", query=f'SOURCE("{table_name}"."{case_column}")'),
               PQLColumn(name="activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
               PQLColumn(name="transition", query=f'SOURCE("{table_name}"."{lifecycle_column}")'),
               PQLColumn(name="resource", query=f'SOURCE("{table_name}"."{resource_column}")')
               ]
    res = execute_PQL_query(data_model, columns)
    return res


def get_unique_activity(df, act_column_name):
    return df[act_column_name].unique()


def get_unique_resource(df, res_column_name):
    return df[res_column_name].unique()


def get_res_act_relation(df, activities):
    res_dict = {}
    for a in activities:
        g1 = df.groupby(["activity"]).get_group(a)
        keys = list(g1.groupby(["resource"]).groups.keys())
        res_dict[a] = keys
    return res_dict


def get_target_activity_with_start_end_timestamp(data_mode, table_name, case_column, activity_column, resource_column,
                                                 timestamp_column):
    columns = [PQLColumn(name="case_id", query=f'SOURCE("{table_name}"."{case_column}")'),
               PQLColumn(name="activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
               PQLColumn(name="resource", query=f'SOURCE("{table_name}"."{resource_column}")'),
               PQLColumn(name="start_at", query=f'SOURCE("{table_name}"."{timestamp_column}")'),
               PQLColumn(name="end_at", query=f'TARGET("{table_name}"."{timestamp_column}")')]
    res = execute_PQL_query(data_mode, columns)
    return res


def encode_activities(data_model, table_name, activity_column):
    col = [PQLColumn(name="activity", query=f'"{table_name}"."{activity_column}"')]
    activities = execute_PQL_query(data_model, col, distinct=True)["activity"]
    num_act = len(activities)
    mapping = dict()
    set1 = string.ascii_letters[:]
    set1 += '0123456789'
    if num_act <= len(set1):
        for i in range(num_act):
            mapping[activities[i]] = set1[i]
        reverse_mapping = {value: key for key, value in mapping.items()}
    else:
        print(f'Too many activities, need to provide more candidates for mapping!')
        return None, None, None
    return mapping, reverse_mapping, activities


def calculate_temporal_profile_task_duration(data_model, table_name, types, case_column, activity_column, time_column,
                                             lifecycle_column, mainstream_case_id=None):
    s = "("
    if mainstream_case_id:
        for idx in mainstream_case_id:
            s += f"\'{idx}\',"
        s = s[:-1]
        s += ")"
    if types == "mainstream":
        filters = [PQLFilter(query=f'FILTER "{table_name}"."{case_column}" IN {s};')]
    elif types == "new":
        filters = [PQLFilter(query=f'FILTER "{table_name}"."{case_column}" NOT IN {s};')]
    else:
        filters = []
    filters.extend([
        PQLFilter(
            query=f'FILTER SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}");'),
        PQLFilter(
            query=f'FILTER SOURCE("{table_name}"."{lifecycle_column}") = \'start\' AND TARGET("{table_name}"."{lifecycle_column}") = \'complete\';')
    ])

    columns_dur1 = [PQLColumn(name="case_id", query=f'SOURCE("{table_name}"."{case_column}")'),
                    PQLColumn(name="activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
                    PQLColumn(name="task_duration(min)",
                              query=f'minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))')
                    ]
    res1 = execute_PQL_query(data_model, columns_dur1, filters=filters)

    cols_dur2 = [PQLColumn(name="Activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
                 PQLColumn(name="max_task_duration(min)",
                           query=f'MAX(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}")))'),
                 PQLColumn(name="min_task_duration(min)",
                           query=f'MIN(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}")))'),
                 PQLColumn(name="mean_task_duration(min)",
                           query=f'ROUND(AVG(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))), 2)'),
                 PQLColumn(name="stdev_task_duration(min)",
                           query=f'ROUND(STDEV(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))), 2)'),
                 PQLColumn(name="var_task_duration(min)",
                           query=f'ROUND(VAR(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))), 2)'),
                 ]

    res2 = execute_PQL_query(data_model, cols_dur2, filters=filters)

    if res1.empty or res2.empty:
        return None, None

    return res2, res1


def calculate_temporal_profile_temporal_distance(data_model, table_name, types, case_column, activity_column,
                                                 time_column,
                                                 lifecycle_column, mainstream_case_id=None):
    """
    Calculate the temporal profile for task duration and time distance
    :param case_column:
    :param mainstream_case_id:
    :param data_model:
    :param table_name:
    :param types: ['overall', 'mainstream', 'new']
    :return:
    """
    s = "("
    if mainstream_case_id:
        for idx in mainstream_case_id:
            s += f"\'{idx}\',"
        s = s[:-1]
        s += ")"
    if types == "mainstream":
        filters = [PQLFilter(query=f'FILTER "{table_name}"."{case_column}" IN {s};')]
    elif types == "new":
        filters = [PQLFilter(query=f'FILTER "{table_name}"."{case_column}" NOT IN {s};')]
    else:
        filters = []
    filters.extend([
        PQLFilter(query=f'FILTER SOURCE("{table_name}"."{lifecycle_column}") != \'start\';')
    ])

    columns_dis1 = [PQLColumn(name="case_id", query=f'SOURCE("{table_name}"."{case_column}")'),
                    PQLColumn(name="start_activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
                    PQLColumn(name="end_activity", query=f'TARGET("{table_name}"."{activity_column}")'),
                    PQLColumn(name="start_life", query=f'SOURCE("{table_name}"."{lifecycle_column}")'),
                    PQLColumn(name="end_life", query=f'TARGET("{table_name}"."{lifecycle_column}")'),
                    PQLColumn(name="temporal_distance(min)",
                              query=f'minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))')
                    ]
    res1 = execute_PQL_query(data_model, columns_dis1, filters=filters)
    cols_dis2 = [PQLColumn(name="Start_Activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
                 PQLColumn(name="End_Activity", query=f'TARGET("{table_name}"."{activity_column}")'),
                 PQLColumn(name="max_temporal_distance(min)",
                           query=f'MAX(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}")))'),
                 PQLColumn(name="min_temporal_distance(min)",
                           query=f'MIN(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}")))'),
                 PQLColumn(name="mean_temporal_distance(min)",
                           query=f'ROUND(AVG(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))), 2)'),
                 PQLColumn(name="stdev_temporal_distance(min)",
                           query=f'ROUND(STDEV(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))), 2)'),
                 PQLColumn(name="var_temporal_distance(min)",
                           query=f'ROUND(VAR(minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))), 2)'),
                 ]
    res2 = execute_PQL_query(data_model, cols_dis2, filters=filters)
    if res1.empty or res2.empty:
        return None, None

    return res2, res1


def trace_cluster(data_model, table_name, case_column, activity_column, resource_column, lifecycle_column):
    columns = [PQLColumn(name="case_id", query=f'("{table_name}"."{case_column}")'),
               PQLColumn(name="activity_trace", query=f'VARIANT("{table_name}"."{activity_column}")'),
               PQLColumn(name="Cluster",
                         query=f'CLUSTER_VARIANTS ( VARIANT ( "{table_name}"."{activity_column}" ) , 2 , 2 )'),
               ]

    res = execute_PQL_query(data_model, columns, distinct=True)

    # Group by 'activity_trace', then aggregate 'case_id' and count
    new_df = res.groupby('activity_trace').agg({'case_id': list}).reset_index()

    # Create a new column, counting the number of 'case_id' for each 'activity_trace'
    new_df['case_count'] = new_df['case_id'].apply(len)

    # Rename column names
    new_df.columns = ['activity_trace', 'case_id_list', 'case_count']

    # Sort by the values in the 'case_count' column in descending order
    new_df = new_df.sort_values('case_count', ascending=False).reset_index(drop=True)

    return new_df


def split_df(df, p=0.2):
    # Calculate the row for the cutoff
    cutoff = int(len(df) * p)

    # Get the 'activity_trace' of the first p percent of rows
    first_p = [[trace] for trace in df['activity_trace'].iloc[:cutoff]]
    first_p_id = []
    for i in df['case_id_list'].iloc[:cutoff]:
        first_p_id.extend(i)
    # Get the 'activity_trace' of the rest of the rows
    rest = [[trace] for trace in df['activity_trace'].iloc[cutoff:]]
    rest_id = []
    for i in df['activity_trace'].iloc[cutoff:]:
        rest_id.extend(i)

    return first_p, first_p_id, rest, rest_id
