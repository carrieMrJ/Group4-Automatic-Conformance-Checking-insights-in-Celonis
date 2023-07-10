def z_score(x, m, s):
    """
    z_score: A function that returns z_score.
    """

    return abs((x - m) / s)


def temporal_deviation_cost_function(x, w, phi, k, a, b, c):
    """
    temporal_deviation_cost_function: A function which calculates temporal deviation cost function.
    """

    z = z_score(x, a, b)
    if c | z < k:
        return 0
    else:
        return z * w * phi


def get_z_score(task_duration, time_distance, temp_profile_dur, temp_profile_dis, k):
    """
    get_z_score
        Args:
            task_duration: A dataframe which contains case_id, activity, task_duration. Return value of a function 'calculate_temporal_profile_task_duration'.
            time_distance: A dataframe which contains case_id, activity, temporal_distance. Return value of a function 'calculate_temporal_profile_temporal_distance'.
            temp_profile_dur: A dataframe which contains max, min, mean, stdev, var of a task durations. Return value of a function 'calculate_temporal_profile_task_duration'.
            temp_profile_dis: A dataframe which contains max, min, mean, stdev, var of a time_distances. Return value of a function 'calculate_temporal_profile_temporal_distance'.
            k: An integer which determines the threshold of a z-score.
        Returns:
            normal_dur: A list with task durations which are not anomaly.
            anomaly_dur: A list with task durations which are anomaly.
            normal_dis: A list with time_distances which are not anomaly.
            anomaly_dis: A list with time_distances which are anomaly.
    """

    normal_dur = list()
    anomaly_dur = list()
    normal_dis = list()
    anomaly_dis = list()

    # find anomalies in task_duration
    if (task_duration is not None) and (temp_profile_dur is not None):
        for index, line in task_duration.iterrows():

            x = line['task_duration(min)']
            y = temp_profile_dur.loc[temp_profile_dur['Activity'] == line['activity']]
            if not y.empty:
                if z_score(x, y['mean_task_duration(min)'].values[0], y['stdev_task_duration(min)'].values[0]) > k:
                    anomaly_dur.append(line)
                else:
                    normal_dur.append(line)
            else:
                anomaly_dur.append(line)

    # find anomalies in time_distance
    if time_distance is not None and temp_profile_dis is not None:
        for index, line in time_distance.iterrows():

            x = line['temporal_distance(min)']
            start = line['start_activity']
            end = line['end_activity']
            y = temp_profile_dis.loc[
                (temp_profile_dis['Start_Activity'] == start) & (temp_profile_dis['End_Activity'] == end)]
            if not y.empty:
                if z_score(x, y['mean_temporal_distance(min)'].values[0], y['stdev_temporal_distance(min)'].values[0]) > k:
                    anomaly_dis.append(line)
                else:
                    normal_dis.append(line)
            else:
                anomaly_dis.append(line)

    return normal_dur, anomaly_dur, normal_dis, anomaly_dis
