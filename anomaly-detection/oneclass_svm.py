from dimensionality_reduction import feature_table_reduced_receipt,feature_table_reduced_review
from preprocessing_ohe import df_review,df_receipt


from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import pandas as pd

#function to calculate anomalies using oneclassSVM and ranking these anomalies based on their score
def oneclassSVM(feature_table_reduced,event_log):

    X_pca=feature_table_reduced
    # Fit a One-Class SVM model to the reduced data
    svm = OneClassSVM(kernel='rbf',degree=3,gamma='scale',nu=0.05)
    svm.fit(X_pca)
    
    # Predict outliers
    y_pred_svm = svm.predict(X_pca)

    # Plot the data points
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c='blue', label='Normal')

    # Plot the anomalies in red color
    anomalies_svm = X_pca[y_pred_svm == -1]
    plt.scatter(anomalies_svm[:, 0], anomalies_svm[:, 1], c='red', label='Anomaly')

    plt.title("Anomaly Detection with One-Class SVM and PCA")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend()
    plt.show()
    
    # Predict outliers/anomalies
    anomaly_scores_svm = svm.decision_function(feature_table_reduced)

    # df with CaseID, Activity, Anomaly Score and Anomaly Label
    case_ranks_svm = pd.DataFrame({'case:concept:name': event_log['case:concept:name'], 'concept:name': event_log['concept:name'], 'AnomalyScore': anomaly_scores_svm, 'AnomalyLabel': y_pred_svm})

    #df for only the anomalies
    only_anomalies_svm=case_ranks_svm[case_ranks_svm['AnomalyLabel']==-1]

    #anomalies sorted based on anomaly score for anomaly ranking
    anomaly_ranked_svm=only_anomalies_svm.sort_values('AnomalyScore')

    # Print the ranked cases
    print(anomaly_ranked_svm)

    return plt.show(),print(anomaly_ranked_svm)

# gives out plot of anomalies in the data and ranks of anomalies based on their scores for review data using oneclassSVM

oneclasssvm_result_review=oneclassSVM(feature_table_reduced_review,df_review)


# gives out plot of anomalies in the data and ranks of anomalies based on their scores for receipt data using oneclassSVM

oneclasssvm_result_receipt=oneclassSVM(feature_table_reduced_receipt,df_receipt)
