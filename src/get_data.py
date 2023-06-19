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

def get_data_for_anomaly_detection_review(data_mode, table_name, case_column, activity_column, resource_column, timestamp_column):
    columns = [PQLColumn(name="Result by Reviewer A", query=f'"{table_name}"."Result by Reviewer A"'),
                PQLColumn(name="Result by Reviewer B", query=f'"{table_name}"."Result by Reviewer B"'),
                PQLColumn(name="Result by Reviewer C", query=f'"{table_name}"."Result by Reviewer C"'),
                PQLColumn(name="Result by Reviewer X", query=f'"{table_name}"."Result by Reviewer X"'),
                PQLColumn(name="accepts", query=f'"{table_name}"."accepts"'),
               PQLColumn(name="case:concept:name", query=f'"{table_name}"."case:concept:name"'),
               PQLColumn(name="case:description", query=f'"{table_name}"."case:description"'),
               PQLColumn(name="concept:name", query=f'"{table_name}"."concept:name"'),
               PQLColumn(name="lifecycle:transition", query=f'"{table_name}"."lifecycle:transition"'),
               PQLColumn(name="org:resource", query=f'"{table_name}"."org:resource"'),
               PQLColumn(name="rejects", query=f'"{table_name}"."rejects"'),
               PQLColumn(name="time:timestamp", query=f'"{table_name}"."time:timestamp"')]

    res=execute_PQL_query(data_mode, columns)

    return res

def get_data_for_anomaly_detection_receipt(data_mode, table_name, case_column, activity_column, resource_column, timestamp_column):
    columns = [PQLColumn(name="case:channel", query=f'"{table_name}"."case:channel"'),
                PQLColumn(name="case:concept:name", query=f'"{table_name}"."case:concept:name"'),
                PQLColumn(name="case:department", query=f'"{table_name}"."case:department"'),
                PQLColumn(name="case:group", query=f'"{table_name}"."case:group"'),
               PQLColumn(name="case:responsible", query=f'"{table_name}"."case:responsible"'),
               PQLColumn(name="concept:instance", query=f'"{table_name}"."concept:instance"'),
               PQLColumn(name="concept:name", query=f'"{table_name}"."concept:name"'),
               PQLColumn(name="lifecycle:transition", query=f'"{table_name}"."lifecycle:transition"'),
               PQLColumn(name="org:group", query=f'"{table_name}"."org:group"'),
               PQLColumn(name="org:resource", query=f'"{table_name}"."org:resource"'),
               PQLColumn(name="time:timestamp", query=f'"{table_name}"."time:timestamp"')]

    res=execute_PQL_query(data_mode, columns)

    return res