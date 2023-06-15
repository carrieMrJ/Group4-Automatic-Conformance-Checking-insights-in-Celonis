import string

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


def mapping_traces(data_model, table_name, activity_column, trace_list):
    def map_activities(data_model_inside, table_name_inside, activity_column_inside):
        col = [PQLColumn(name="activity", query=f'"{table_name_inside}"."{activity_column_inside}"')]
        activities = execute_PQL_query(data_model_inside, col, distinct=True)["activity"]
        num_act = len(activities)
        mapping_inside = dict()
        set1 = string.ascii_letters[:]
        set1 += '0123456789'
        if num_act <= len(set1):
            for i in range(num_act):
                mapping_inside[activities[i]] = set1[i]
        else:
            return f'Too many activities, need to provide more candidates for mapping!'
        return mapping_inside, activities

    mapping, act_l = map_activities(data_model, table_name, activity_column)
    print(mapping)
    # col2 = [PQLColumn(name="activity_trace", query=f'VARIANT("{table_name}"."{activity_column}")')]
    # main_trace_list = execute_PQL_query(data_model, col2, distinct=True)["activity_trace"]
    traces = []
    for t in trace_list:
        tmp = t.split(", ")
        trace = ""
        for act in tmp:
            trace += mapping[act]
        traces.append(trace)
    return traces, mapping, list(mapping.values())



