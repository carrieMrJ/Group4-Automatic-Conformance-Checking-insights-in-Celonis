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

def trace_cluster(data_model, table_name, case_column, activity_column, resource_column, lifecycle_column):


    columns = [PQLColumn(name="case_id", query=f'("{table_name}"."{case_column}")'),
               PQLColumn(name="activity_trace", query=f'VARIANT("{table_name}"."{activity_column}")'),
               PQLColumn(name="Cluster", query=f'CLUSTER_VARIANTS ( VARIANT ( "{table_name}"."{activity_column}" ) , 2 , 2 )'),
              ]

    res = execute_PQL_query(data_model, columns, distinct=True)
    return res 

def split_df(df, p=0.2):
    # Calculate the row for the cutoff
    cutoff = int(len(df) * p)
    
    # Get the 'activity_trace' of the first p percent of rows
    first_p = [[trace] for trace in df['activity_trace'].iloc[:cutoff]]
    
    # Get the 'activity_trace' of the rest of the rows
    rest = [[trace] for trace in df['activity_trace'].iloc[cutoff:]]
    
    return first_p, rest
