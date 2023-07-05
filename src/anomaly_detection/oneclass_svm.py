from sklearn.svm import OneClassSVM
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

#function to calculate anomalies using oneclassSVM and ranking these anomalies based on their score
def oneclassSVM(feature_table_reduced,event_log):
    """
    Applies the oneclasssvm algorithm to the features and gives out the anomalies as well as ranks those anomalies based on their anomaly score.
    :param df: dataframe which has reduced dimensions from dimensionality_reduction
    :return: a plot showing the anomalies in the data and the ranked anomalies with their caseid, acitivity and anomaly score.  
 
    """
    X_pca=feature_table_reduced
    # Fit a One-Class SVM model to the reduced data
    svm = OneClassSVM(kernel='rbf',degree=3,gamma='scale',nu=0.05)
    svm.fit(X_pca)
    
    # Predict outliers
    y_pred_svm = svm.predict(X_pca)

    # Plot the data points
    #plt.scatter(X_pca[:, 0], X_pca[:, 1], c='blue', label='Normal')

    # Plot the anomalies in red color
    anomalies_svm = X_pca[y_pred_svm == -1]
    '''plt.scatter(anomalies_svm[:, 0], anomalies_svm[:, 1], c='red', label='Anomaly')

    plt.title("Anomaly Detection with One-Class SVM and PCA")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend()'''
    #plt.show()
    
    # Predict outliers/anomalies
    anomaly_scores_svm = svm.decision_function(feature_table_reduced)

    # df with CaseID, Activity, Anomaly Score and Anomaly Label
    case_ranks_svm = pd.DataFrame({'case:concept:name': event_log['case:concept:name'], 'concept:name': event_log['concept:name'], 'AnomalyScore': anomaly_scores_svm, 'AnomalyLabel': y_pred_svm})

    #df for only the anomalies
    only_anomalies_svm=case_ranks_svm[case_ranks_svm['AnomalyLabel']==-1]

    #anomalies sorted based on anomaly score for anomaly ranking
    anomaly_ranked_svm=only_anomalies_svm.sort_values('AnomalyScore')

    # Print the ranked cases
    

    return anomalies_svm, anomaly_ranked_svm


'''
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
'''