#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd
import pycelonis
import yaml
from pycelonis.pql import PQL, PQLColumn, PQLFilter, OrderByColumn
from pycelonis_core.utils.errors import PyCelonisNotFoundError
import numpy as np
from collections import defaultdict
from src.data_integration.celonis_data_integration import get_connection, get_celonis_info, create_pool_and_model, check_invalid_table_in_celonis, execute_PQL_query
from src.data_integration.get_data import get_execution_time_per_res_per_act, get_unique_activity, get_unique_resource, get_res_act_relation, get_target_activity_with_start_end_timestamp 
from src.resource_based.resource_performance import resource_performance
from src.resource_based.batch_identification import batch_identification
from src.data_integration.get_data import get_caseid_activity_lifecycle_resource
from src.resource_based.find_high_rework_resources_analysis import find_high_rework_resources
from src.resource_based.find_deviations_analysis import find_deviations


# In[10]:


def resource_based_overall(celonis, table, rework_threshold=1, count_threshold=2, deviations_threshold=1):
    # get the data pool and data model of our project
    data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name, lifecycle = get_celonis_info(
        celonis=celonis)

    # check if one table is invalid (does not exist in our data pool/model)
    if not check_invalid_table_in_celonis(data_model, table):
        df = get_execution_time_per_res_per_act(data_model, table, case_column_name, act_column_name,
                                                res_column_name, time_column_name)
    else:
        print(f"No such table")
        return None

    le, me = resource_performance(df)

    batch_data = get_target_activity_with_start_end_timestamp(data_model, table, case_column_name, act_column_name,
                                                res_column_name, time_column_name)
    resources = get_unique_resource(batch_data, "resource")
    activities = get_unique_activity(batch_data, "activity")

    import warnings
    warnings.filterwarnings('ignore')

    df_sim, df_seq, df_con = batch_identification(batch_data, activities)

    df = get_caseid_activity_lifecycle_resource(data_model, table, case_column_name, act_column_name, res_column_name, lifecycle)

    # find high rework resources
    high_rework_resources = find_high_rework_resources(df, rework_threshold, count_threshold)

    # get data using PQL
    df = get_caseid_activity_lifecycle_resource(data_model, table, case_column_name, act_column_name, res_column_name, lifecycle)

    deviations = find_deviations(df, deviations_threshold)

    return le, me, df_sim, df_seq, df_con, high_rework_resources, deviations

