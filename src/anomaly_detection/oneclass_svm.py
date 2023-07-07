from sklearn.svm import OneClassSVM
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

def oneclassSVM(feature_table_reduced,event_log):
    """
    Applies the oneclasssvm algorithm to the features and gives out the anomalies as well as ranks those anomalies based on their anomaly score.
    :param df: dataframe which has reduced dimensions from dimensionality_reduction
    :return: a plot showing the anomalies in the data and the ranked anomalies with their caseid, acitivity and anomaly score.  
 
    """
    X_pca=feature_table_reduced
    svm = OneClassSVM(kernel='rbf',degree=3,gamma='scale',nu=0.05)
    svm.fit(X_pca)

    y_pred_svm = svm.predict(X_pca)

    anomalies_svm = X_pca[y_pred_svm == -1]

    anomaly_scores_svm = svm.decision_function(feature_table_reduced)

    case_ranks_svm = pd.DataFrame({'case:concept:name': event_log['case:concept:name'], 'concept:name': event_log['concept:name'], 'AnomalyScore': anomaly_scores_svm, 'AnomalyLabel': y_pred_svm})

    only_anomalies_svm=case_ranks_svm[case_ranks_svm['AnomalyLabel']==-1]

    anomaly_ranked_svm=only_anomalies_svm.sort_values('AnomalyScore')

    return anomalies_svm, anomaly_ranked_svm