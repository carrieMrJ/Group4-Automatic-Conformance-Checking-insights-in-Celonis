
def resource_performance(df):
    """
    Find the most efficient resource and the least efficient resource for each activity
    :param df: dataframe with activity, resource, and execution time
    :return:
    two dataframes: 1. the least efficient resource for each activity and their average execution time 2. the most
    efficient resource for each activity and their average execution time
    """
    # calculate the total execution time and times of each activity executed by each resource
    avg_time_df = df.groupby(["source_act", "source_resource"]).agg({"time_between": ["sum", "count"]}).reset_index()
    avg_time_df.columns = ["source_act", "source_resource", "total_time", "count"]
    # calculate the average execution time for each resource of each activity
    avg_time_df["avg_time"] = avg_time_df["total_time"] / avg_time_df["count"]
    # the least efficient
    least_efficient = avg_time_df[["source_act", "source_resource", "avg_time"]].groupby(["source_act"],
                                                                                         as_index=False).max()
    least_efficient.columns = ["activity", "the least efficient resource", "avg_execution_time(min)"]
    # the most efficient
    most_efficient = avg_time_df[["source_act", "source_resource", "avg_time"]].groupby(["source_act"],
                                                                                        as_index=False).min()
    most_efficient.columns = ["activity", "the most efficient resource", "avg_execution_time(min)"]

    return least_efficient, most_efficient

