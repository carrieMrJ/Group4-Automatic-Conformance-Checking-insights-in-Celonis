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


