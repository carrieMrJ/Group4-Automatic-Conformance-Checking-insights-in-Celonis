from pycelonis.pql import PQLColumn, PQLFilter
from src.data_integration.celonis_data_integration import execute_PQL_query

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