import pandas as pd
import pycelonis
import yaml
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.decomposition import PCA
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import make_column_selector as selector
from sklearn.compose import make_column_transformer 
from sklearn.compose import ColumnTransformer
from pycelonis.pql import PQL, PQLColumn, PQLFilter, OrderByColumn
from pycelonis_core.utils.errors import PyCelonisNotFoundError
from collections import defaultdict
from src.get_data import get_data_for_anomaly_detection_receipt,get_data_for_anomaly_detection_review,get_celonis_info
from anomaly_detection.dimensionality_reduction import pca
from anomaly_detection.preprocessing_ohe import preprocessing_receipt,preprocessing_review
from anomaly_detection.isolation_forests import isolation_forests
from anomaly_detection.oneclass_svm import oneclassSVM

def anomaly_detection_receipt(celonis, table,):
    # get the data pool and data model of our project
    data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name, lifecycle = get_celonis_info(
        celonis=celonis)


    df_receipt=get_data_for_anomaly_detection_receipt(data_model, table, case_column_name, act_column_name,
                                                res_column_name, time_column_name)
    
    # df with preprocessed receipt data
    df_pre_receipt=preprocessing_receipt(df_receipt)

    # df with receipt feature table after dimensionality reduction
    feature_table_reduced_receipt=pca(df_pre_receipt)

    # gives out plot of anomalies in the data and ranks of anomalies based on their scores for receipt data using isolation forest
    if_result_receipt=isolation_forests(feature_table_reduced_receipt,df_receipt)

    # gives out plot of anomalies in the data and ranks of anomalies based on their scores for receipt data using oneclassSVM
    oneclasssvm_result_receipt=oneclassSVM(feature_table_reduced_receipt,df_receipt)

    return if_result_receipt,oneclasssvm_result_receipt

def anomaly_detection_review(celonis, table,):
        # get the data pool and data model of our project
    data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name, lifecycle = get_celonis_info(
        celonis=celonis)

    
    df_review=get_data_for_anomaly_detection_review(data_model, table, case_column_name, act_column_name,
                                                res_column_name, time_column_name)
    
    # df with preprocessed review data
    df_pre_review=preprocessing_review(df_review)

    # df of review with feature table after dimensionality reduction
    feature_table_reduced_review=pca(df_pre_review)

    # gives out plot of anomalies in the data and ranks of anomalies based on their scores for review data using isolation forests
    if_result_review=isolation_forests(feature_table_reduced_review,df_review)

    # gives out plot of anomalies in the data and ranks of anomalies based on their scores for review data using oneclassSVM
    oneclasssvm_result_review=oneclassSVM(feature_table_reduced_review,df_review)
    
    return if_result_review,oneclasssvm_result_review
    