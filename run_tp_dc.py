from src.data_integration.get_data import trace_cluster, split_df, get_task_duration_time_distance, \
    calculate_temporal_profile_task_duration, calculate_temporal_profile_time_distance, encode_activities
from src.declarative_constraints.constraint_operations import constraints_generation, event_log_constraint_extraction
from src.temporal_profile.deviation_based_on_z_score import get_z_score
from src.anomaly_detection.get_datas import get_data_for_anomaly_detection_receipt, get_data_for_anomaly_detection_review
from src.anomaly_detection.preprocessing_ohe import preprocessing_receipt, preprocessing_review
from src.anomaly_detection.dimensionality_reduction import pca
from src.anomaly_detection.isolation_forests import isolation_forests
from src.anomaly_detection.oneclass_svm import oneclassSVM

def get_variants_info(data_model, table_name, case_column, activity_column, resource_column, lifecycle_column):
    return trace_cluster(data_model, table_name, case_column, activity_column, resource_column, lifecycle_column)


def get_standard_behavior(variants_info, percentage_of_variant):
    main, main_id, new, new_id = split_df(variants_info, percentage_of_variant)
    return main, main_id, new, new_id


def temporal_profile_analysis(data_pool, data_model, table_name, case_column, activity_column, time_column,
                              lifecycle_column, mainstream_id):
    task_duration, time_distance = get_task_duration_time_distance(data_pool, data_model, table_name,
                                                                   case_column=case_column,
                                                                   activity_column=activity_column,
                                                                   time_column=time_column,
                                                                   lifecycle_column=lifecycle_column)

    temporal_profile_task_dur_all, all_task_dur = calculate_temporal_profile_task_duration(data_model, table_name,
                                                                                           "overall", "case_id",
                                                                                           mainstream_id)

    temporal_profile_time_dis_all, all_time_dis = calculate_temporal_profile_time_distance(data_model, table_name,
                                                                                           "overall", "case_id",
                                                                                           mainstream_id)

    temporal_profile_task_dur_main, main_task_dur = calculate_temporal_profile_task_duration(data_model, table_name,
                                                                                             "mainstream", "case_id",
                                                                                             mainstream_id)

    temporal_profile_dis_main, main_dis = calculate_temporal_profile_time_distance(data_model, table_name, "mainstream",
                                                                                   "case_id", mainstream_id)

    temporal_profile_task_dur_new, new_task_dur = calculate_temporal_profile_task_duration(data_model, table_name,
                                                                                           "new", "case_id",
                                                                                           mainstream_id)

    temporal_profile_time_dis_new, new_time_dis = calculate_temporal_profile_time_distance(data_model, table_name,
                                                                                           "new", "case_id",
                                                                                           mainstream_id)

    return temporal_profile_task_dur_all, all_task_dur, temporal_profile_time_dis_all, all_time_dis, temporal_profile_task_dur_main, main_task_dur, temporal_profile_dis_main, main_dis, temporal_profile_task_dur_new, new_task_dur, temporal_profile_time_dis_new, new_time_dis


def temporal_profile_deviations(new_task_dur, new_time_dis, temporal_profile_task_dur_main,
                                temporal_profile_time_dis_main, threshold_z):
    normal_dur, anomaly_dur, normal_dis, anomaly_dis = get_z_score(new_task_dur, new_time_dis,
                                                                   temporal_profile_task_dur_main,
                                                                   temporal_profile_time_dis_main, threshold_z)
    return normal_dur, anomaly_dur, normal_dis, anomaly_dis


def declarative_constraint_analysis(data_model, table_name, activity_column, constraint_names, constraint_library,
                                    variants_info, percentage_of_instances=0.5):
    mapping, reverse, activities = encode_activities(data_model, table_name, activity_column)
    constraint_list = constraints_generation(list(mapping.values()), constraint_names, constraint_library)
    constraints_extracted = event_log_constraint_extraction(variants_info, constraint_list, constraint_library,
                                                            percentage_of_instances, mapping, reverse)
    return constraints_extracted

def anomaly_detection(data_model, table_name, case_column_name, act_column_name, res_column_name, time_column_name):

    if table_name=='reviewing':
        df=get_data_for_anomaly_detection_review(data_model, table_name, case_column_name, act_column_name, res_column_name, time_column_name)
    if table_name=='receipt':
        df=get_data_for_anomaly_detection_receipt(data_model, table_name, case_column_name, act_column_name, res_column_name, time_column_name)
    
    return df

def anomaly_tables(table_name, df):
    if table_name=='reviewing':
        pre=preprocessing_review(df)
    if table_name=='receipt':
        pre=preprocessing_receipt(df)
    
    pca_table=pca(pre)

    a_if, ar_if = isolation_forests(pca_table, df)
    a_svm, ar_svm = oneclassSVM(pca_table, df)

    return pre, pca_table, a_if, ar_if, a_svm, ar_svm