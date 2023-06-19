from dimensionality_reduction import feature_table_reduced_receipt,feature_table_reduced_review
from preprocessing_ohe import df_review,df_receipt


from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import pandas as pd

#function to calculate anomalies using isolation forests and ranking these anomalies based on their score
def isolation_forests(feature_table_reduced,event_log):
    """
    Applies the isolation forest algorithm to the features and gives out the anomalies as well as ranks those anomalies based on their anomaly score.
    :param df: dataframe which has reduced dimensions from dimensionality_reduction
    :return: a plot showing the anomalies in the data and the ranked anomalies with their caseid, acitivity and anomaly score.  
 
    """

    # Apply anomaly detection using Isolation Forest
    isolation_forest = IsolationForest(n_estimators=100,contamination=0.05,bootstrap=False)
    isolation_forest.fit(feature_table_reduced)

    # Predict outliers
    y_pred_if = isolation_forest.predict(feature_table_reduced)

    # Plot the data points
    plt.scatter(feature_table_reduced[:, 0], feature_table_reduced[:, 1], c='blue', label='Normal')

    # Plot the anomalies in red color
    anomalies_if = feature_table_reduced[y_pred_if == -1]
    plt.scatter(anomalies_if[:, 0], anomalies_if[:, 1], c='red', label='Anomaly')

    plt.title("Anomaly Detection with Isolation Forest and PCA")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend()
    plt.show()
    
    # Predict outliers/anomalies
    anomaly_scores_if = isolation_forest.decision_function(feature_table_reduced)

    # Rank cases based on anomaly scores
    case_ranks_if = pd.DataFrame({'case:concept:name': event_log['case:concept:name'], 'concept:name':event_log['concept:name'], 'AnomalyScore': anomaly_scores_if, 'AnomalyLabel':y_pred_if})

    #df for only the anomalies
    only_anomalies_if=case_ranks_if[case_ranks_if['AnomalyLabel']==-1]

    #anomalies sorted based on anomaly score for anomaly ranking
    anomaly_ranked_if=only_anomalies_if.sort_values('AnomalyScore')

    # Print the ranked anomalies with their caseID,Activity,AnomalyScore and AnomalyLabel
    print(anomaly_ranked_if)

    return plt.show(),print(anomaly_ranked_if)

# gives out plot of anomalies in the data and ranks of anomalies based on their scores for review data using isolation forests
if_result_review=isolation_forests(feature_table_reduced_review,df_review)


# gives out plot of anomalies in the data and ranks of anomalies based on their scores for receipt data using isolation forest
if_result_receipt=isolation_forests(feature_table_reduced_receipt,df_receipt)