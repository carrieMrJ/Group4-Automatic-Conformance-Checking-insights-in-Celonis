#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

def find_deviations(df, threshold):
    # Determine the "usual" activities for each resource
    usual_activities = df.groupby('resource')['activity'].value_counts()
    
    # Filter the usual activities based on a threshold
    usual_activities = usual_activities[usual_activities > threshold].reset_index(name='count').groupby('resource')['activity'].apply(set)

    # Track the activities of each resource in the log
    for case in df['case_id'].unique():
        case_df = df[df['case_id'] == case]
        for idx, row in case_df.iterrows():
            resource = row['resource']
            activity = row['activity']

            # If a resource executes an activity that is not in their usual set, flag it
            if activity not in usual_activities.get(resource, set()):
                print(f'Deviation found: Resource {resource} performed unusual activity {activity} in case {case}')

