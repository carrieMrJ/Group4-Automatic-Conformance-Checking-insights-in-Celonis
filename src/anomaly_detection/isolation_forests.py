from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

def isolation_forests(feature_table_reduced,event_log):
    """
    Applies the isolation forest algorithm to the features and gives out the anomalies as well as ranks those anomalies based on their anomaly score.
    :param df: dataframe which has reduced dimensions from dimensionality_reduction
    :return: a plot showing the anomalies in the data and the ranked anomalies with their caseid, acitivity and anomaly score.  
 
    """

    isolation_forest = IsolationForest(n_estimators=100,contamination=0.05,bootstrap=False)
    isolation_forest.fit(feature_table_reduced)

    y_pred_if = isolation_forest.predict(feature_table_reduced)

    anomalies_if = feature_table_reduced[y_pred_if == -1]

    anomaly_scores_if = isolation_forest.decision_function(feature_table_reduced)

    case_ranks_if = pd.DataFrame({'case:concept:name': event_log['case:concept:name'], 'concept:name':event_log['concept:name'], 'AnomalyScore': anomaly_scores_if, 'AnomalyLabel':y_pred_if})

    only_anomalies_if=case_ranks_if[case_ranks_if['AnomalyLabel']==-1]

    anomaly_ranked_if=only_anomalies_if.sort_values('AnomalyScore')

    return anomalies_if, anomaly_ranked_if
