from pycelonis.pql import PQLColumn

from src.celonis_data_integration import execute_PQL_query, get_connection, check_invalid_table_in_celonis, \
    get_celonis_info

from src.get_data.py import get_data_for_anomaly_detection_receipt,get_data_for_anomaly_detection_review


import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import make_column_selector as selector
from sklearn.compose import make_column_transformer 
from sklearn.compose import ColumnTransformer

df_review=get_data_for_anomaly_detection_review(data_mode, table_name, case_column, activity_column, resource_column, timestamp_column)

df_receipt=get_data_for_anomaly_detection_receipt(data_mode, table_name, case_column, activity_column, resource_column, timestamp_column)




#function to preprocess review data along with ohe
def preprocessing_review(df):
    df_new=df
    df_new['accepts'] = df_new['accepts'].fillna(0)
    df_new['rejects'] = df_new['rejects'].fillna(0)

    for i in enumerate(df_new["time:timestamp"]):
        a=df_new["time:timestamp"][i[0]]
        df_new["time:timestamp"][i[0]]=pd.Timestamp(a).timestamp()

    categorical_preprocessor = OneHotEncoder(handle_unknown="ignore")
    numerical_preprocessor = StandardScaler()

    numerical_columns_selector = selector(dtype_exclude=object)
    categorical_columns_selector = selector(dtype_include=object)

    numerical_columns = numerical_columns_selector(df_new)
    categorical_columns = categorical_columns_selector(df_new)

    preprocessor = ColumnTransformer([
        ('one-hot-encoder', categorical_preprocessor, categorical_columns),
        ('standard_scaler', numerical_preprocessor, numerical_columns)])

    preprocessor.fit(df_new)
    X1= preprocessor.transform(df_new)

    transformer = make_column_transformer(
        (OneHotEncoder(sparse_output=False), ['Result by Reviewer A', 'Result by Reviewer B', 'Result by Reviewer C',
                           'Result by Reviewer X', 'concept:name', 'lifecycle:transition', 'org:resource','case:description']),
        remainder='passthrough')
    

    transformed = transformer.fit_transform(df_new)
    df_new = pd.DataFrame(transformed, columns=transformer.get_feature_names_out())

    return df_new


df_pre_review=preprocessing_review(df_review)
