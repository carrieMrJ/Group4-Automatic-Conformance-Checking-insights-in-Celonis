#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def find_high_rework_resources(data, rework_threshold=1, count_threshold=4):
    data['activity'] = data['activity'] + "_" + data['transition']

    # Count unique resources for each case-activity combination
    task_counts = data.groupby(['case_id', 'activity'])['resource'].nunique()

    # Filter tasks where count > 1, meaning they are performed by more than one resource within the case
    repeated_tasks = task_counts[task_counts > rework_threshold]

    # Filter the original data to only include tasks identified as repeated
    high_rework = data[data.set_index(['case_id', 'activity']).index.isin(repeated_tasks.index)]

    # Collect all timestamps for each case-activity-resource combination
    rework_resources = high_rework.groupby(['case_id', 'activity', 'resource']).size().reset_index(name='Count')
    df_more_than_3 = rework_resources[rework_resources['Count'] > count_threshold]
    resource_list = df_more_than_3['resource'].unique().tolist()

    return resource_list

