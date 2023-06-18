def z_score(x,m,s):
    """
    z_score: A function that returns z_score.
    """

    return abs((x-m)/s)

def temporal_deviation_cost_function(x,w,phi,k,a,b,c):
    """
    temporal_deviation_cost_function: A function which calculates temporal deviation cost function.
    """

    z=z_score(x,a,b)
    if c | z<k:
        return 0
    else:
        return z*w*phi

def get_z_score(task_duration, time_distance, temp_profile_dur, temp_profile_dis, k):
    """
    get_z_score
        Args:
            task_duration: A dataframe which contains case_id, activity, task_duration. Return value of a function 'get_task_duration_time_distance'.
            time_distance: A dataframe which contains case_id, activity, time_distance. Return value of a function 'get_task_duration_time_distance'.
            temp_profile_dur: A dataframe which contains max, min, mean, stdev, var of a task durations. Return value of a function 'calculate_temporal_profile'.
            temp_profile_dis: A dataframe which contains max, min, mean, stdev, var of a time_distances. Return value of a function 'calculate_temporal_profile'.
            k: An integer which determines the threshold of a z-score.
        Returns:
            normal_dur: A list with task durations which are not anomaly.
            anomaly_dur: A list with task durations which are anomaly.
            normal_dis: A list with time_distances which are not anomaly.
            anomaly_dis: A list with time_distances which are anomaly.
    """

    normal_dur=list()
    anomaly_dur=list()
    normal_dis=list()
    anomaly_dis=list()
    
    #find anomalies in task_duration
    for index,line in task_duration.iterrows():

        x=line['task_duration(min)']
        y=temp_profile_dur.loc[temp_profile_dur['Activity']==line['start_activity']]

        if z_score(x,y['mean_task_duration(min)'][0],y['stdev_task_duration(min)'][0])>k:
            anomaly_dur.append(line)
        else:
            normal_dur.append(line)
    
    #find anomalies in time_distance
    for index,line in time_distance.iterrows():

        x=line['time_distance(min)']
        y=temp_profile_dis.loc[temp_profile_dis['Activity']==line['start_activity']+line['end_activity']]

        if z_score(x,y['mean_time_distance(min)'][0],y['stdev_time_distance(min)'][0])>k:
            anomaly_dis.append(line)
        else:
            normal_dis.append(line)
        
    return normal_dur,anomaly_dur,normal_dis,anomaly_dis