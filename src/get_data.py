from pycelonis.pql import PQLColumn, PQLFilter
import pycelonis
from src.celonis_data_integration import execute_PQL_query, get_connection, check_invalid_table_in_celonis, \
    get_celonis_info


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


def get_task_duration_time_distance(data_pool, data_model, table_name, case_column, activity_column, time_column,
                                    lifecycle_column):
    """
    Get task duration for a certain activity and
    time distance between different/multiple-tries activities that act as souce and target on DFG
    :param data_pool:
    :param data_model:
    :param table_name:
    :param case_column:
    :param activity_column:
    :param time_column:
    :param lifecycle_column:
    :return: Two data frame: One for task duration (only for tasks that have start and complete life status);
    the other one for time distance (between activities act as source and target on DFG)
    """

    columns_dur = [PQLColumn(name="case_id", query=f'SOURCE("{table_name}"."{case_column}")'),
                   PQLColumn(name="start_activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
                   PQLColumn(name="end_activity", query=f'TARGET("{table_name}"."{activity_column}")'),
                   PQLColumn(name="start_life", query=f'SOURCE("{table_name}"."{lifecycle_column}")'),
                   PQLColumn(name="end_life", query=f'TARGET("{table_name}"."{lifecycle_column}")'),
                   PQLColumn(name="task_duration(min)",
                             query=f'minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))')
                   ]
    filter_dur = [
        PQLFilter(
            query=f'FILTER SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}");'),
        PQLFilter(
            query=f'FILTER SOURCE("{table_name}"."{lifecycle_column}") = \'start\' AND TARGET("{table_name}"."{lifecycle_column}") = \'complete\';')
    ]
    res_task_duration = execute_PQL_query(data_model, columns_dur, filters=filter_dur)
    if not res_task_duration.empty:
        try:
            data_pool_table = data_pool.get_tables().find(f'{table_name}_task_duration')
        except PyCelonisNotFoundError:
            data_pool.create_table(df=res_task_duration, table_name=f'{table_name}_task_duration',
                                   drop_if_exists=False)
            data_model.add_table(name=f'{table_name}_task_duration', alias=f'{table_name}_task_duration')
        else:
            data_pool_table.upsert(res_task_duration, keys=["case_id", "start_activity", "end_activity"])
        data_model.reload()

    columns_dis = [PQLColumn(name="case_id", query=f'SOURCE("{table_name}"."{case_column}")'),
                   PQLColumn(name="start_activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
                   PQLColumn(name="end_activity", query=f'TARGET("{table_name}"."{activity_column}")'),
                   PQLColumn(name="start_life", query=f'SOURCE("{table_name}"."{lifecycle_column}")'),
                   PQLColumn(name="end_life", query=f'TARGET("{table_name}"."{lifecycle_column}")'),
                   PQLColumn(name="start_timestamp", query=f'SOURCE("{table_name}"."{time_column}")'),
                   PQLColumn(name="end_timestamp", query=f'TARGET("{table_name}"."{time_column}")'),
                   PQLColumn(name="time_distance(min)",
                             query=f'minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}"))')
                   ]
    filter_dis = [
        PQLFilter(query=f'FILTER SOURCE("{table_name}"."{lifecycle_column}") != \'start\';')
    ]
    res_time_distance = execute_PQL_query(data_model, columns_dis, filters=filter_dis)
    if not res_time_distance.empty:
        try:
            data_pool_table = data_pool.get_tables().find(f'{table_name}_time_distance')
        except PyCelonisNotFoundError:
            data_pool.create_table(df=res_task_duration, table_name=f'{table_name}_time_distance',
                                   drop_if_exists=False)
            data_model.add_table(name=f'{table_name}_task_duration', alias=f'{table_name}_time_distance')
        else:
            data_pool_table.upsert(res_time_distance, keys=["case_id", "start_activity", "end_activity"])
        data_model.reload()

    return res_task_duration, res_time_distance


def calculate_temporal_profile(data_model, table_name, types, case_column, mainstream_case_id=None):
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
        for id in mainstream_case_id:
            s += f"\'{id}\',"
        s = s[:-1]
        s += ")"
    if types == "mainstream":
        filters = [PQLFilter(query=f'FILTER "{table_name}_task_duration"."{case_column}" IN {s};')]
    elif types == "new":
        filters = [PQLFilter(query=f'FILTER "{table_name}_task_duration"."{case_column}" NOT IN {s};')]
    else:
        filters = []

    cols_dur = [PQLColumn(name="Activity", query=f'"{table_name}_task_duration"."start_activity"'),
                PQLColumn(name="max_task_duration(min)",
                          query=f'MAX("{table_name}_task_duration"."task_duration(min)")'),
                PQLColumn(name="min_task_duration(min)",
                          query=f'MIN("{table_name}_task_duration"."task_duration(min)")'),
                PQLColumn(name="mean_task_duration(min)",
                          query=f'ROUND(AVG("{table_name}_task_duration"."task_duration(min)"), 2)'),
                PQLColumn(name="stdev_task_duration(min)",
                          query=f'ROUND(STDEV("{table_name}_task_duration"."task_duration(min)"), 2)'),
                PQLColumn(name="var_task_duration(min)",
                          query=f'ROUND(VAR("{table_name}_task_duration"."task_duration(min)"), 2)'),
                ]
    res_dur = execute_PQL_query(data_model, cols_dur, filters=filters)

    cols_dis = [PQLColumn(name="Start_activity", query=f'"{table_name}_time_distance"."start_activity"'),
                PQLColumn(name="End_activity", query=f'"{table_name}_time_distance"."end_activity"'),
                PQLColumn(name="max_time_distance(min)",
                          query=f'MAX("{table_name}_time_distance"."time_distance(min)")'),
                PQLColumn(name="min_time_distance(min)",
                          query=f'MIN("{table_name}_time_distance"."time_distance(min)")'),
                PQLColumn(name="mean_time_distance(min)",
                          query=f'ROUND(AVG("{table_name}_time_distance"."time_distance(min)"), 2)'),
                PQLColumn(name="stdev_time_distance(min)",
                          query=f'ROUND(STDEV("{table_name}_time_distance"."time_distance(min)"), 2)'),
                PQLColumn(name="var_time_distance(min)",
                          query=f'ROUND(VAR("{table_name}_time_distance"."time_distance(min)"), 2)'),
                ]
    res_dis = execute_PQL_query(data_model, cols_dis, filters=filters)
    return res_dur, res_dis



def trace_cluster(data_model, table_name, case_column, activity_column, resource_column, lifecycle_column):


    columns = [PQLColumn(name="case_id", query=f'("{table_name}"."{case_column}")'),
               PQLColumn(name="activity_trace", query=f'VARIANT("{table_name}"."{activity_column}")'),
               PQLColumn(name="Cluster", query=f'CLUSTER_VARIANTS ( VARIANT ( "{table_name}"."{activity_column}" ) , 2 , 2 )'),
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
    
    # Get the 'activity_trace' of the rest of the rows
    rest = [[trace] for trace in df['activity_trace'].iloc[cutoff:]]
    
    return first_p, rest

