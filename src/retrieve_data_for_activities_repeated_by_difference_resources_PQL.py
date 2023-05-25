#!/usr/bin/env python
# coding: utf-8

# In[2]:


from pycelonis.pql import PQLColumn

from celonis_data_integration import execute_PQL_query, get_connection, check_invalid_table_in_celonis,     get_celonis_info


# In[32]:


def get_caseid_activity_lifecycle_resource(data_model, table_name, case_column, activity_column, resource_column,
                                       lifecycle_column):
    columns = [PQLColumn(name="case_id", query=f'SOURCE("{table_name}"."{case_column}")'),
               PQLColumn(name="activity", query=f'SOURCE("{table_name}"."{activity_column}")'),
               PQLColumn(name="transition", query=f'SOURCE("{table_name}"."{lifecycle_column}")'),
               PQLColumn(name="resource", query=f'SOURCE("{table_name}"."{resource_column}")')
              ]
    res = execute_PQL_query(data_model, columns)
    return res

