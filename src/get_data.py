from pycelonis.pql import PQLColumn

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


def get_task_duration_time_distance(data_model, table_name, case_column, activity_column, time_column,
                                    lifecycle_column):
    """
    Get task duration for a certain activity and
    time distance between different/multiple-tries activities that act as souce and target on DFG
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
                   PQLColumn(name="start_activity",
                             query=f'CASE WHEN SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}") THEN SOURCE("{table_name}"."{activity_column}") END'),
                   PQLColumn(name="end_activity",
                             query=f'CASE WHEN SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}") THEN TARGET("{table_name}"."{activity_column}") END'),
                   PQLColumn(name="start_life",
                             query=f'CASE WHEN SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}") THEN SOURCE("{table_name}"."{lifecycle_column}") END'),
                   PQLColumn(name="end_life",
                             query=f'CASE WHEN SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}") THEN TARGET("{table_name}"."{lifecycle_column}") END'),
                   PQLColumn(name="start_timestamp",
                             query=f'CASE WHEN SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}") THEN SOURCE("{table_name}"."{time_column}") END'),
                   PQLColumn(name="end_timestamp",
                             query=f'CASE WHEN SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}") THEN TARGET("{table_name}"."{time_column}") END'),
                   PQLColumn(name="task_duration(min)",
                             query=f'CASE WHEN SOURCE("{table_name}"."{activity_column}") = TARGET("{table_name}"."{activity_column}") THEN minutes_between(SOURCE("{table_name}"."{time_column}"), TARGET("{table_name}"."{time_column}")) ELSE NULL END')
                   ]
    res_task_duration = execute_PQL_query(data_model, columns_dur)
    res_task_duration = res_task_duration.dropna(axis=0, how='any')
    res_task_duration = res_task_duration[res_task_duration.start_life == "start"]

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
    res_time_distance = execute_PQL_query(data_model, columns_dis)
    res_time_distance = res_time_distance[res_time_distance["start_life"] != "start"]

    return res_task_duration, res_time_distance
