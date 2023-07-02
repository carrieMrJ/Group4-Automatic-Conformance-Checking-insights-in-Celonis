from preprocessing_ohe import df_pre_receipt,df_pre_review

from sklearn.decomposition import PCA
import pandas as pd


def pca(df):
    
    """
    Reducing dimensions using principle component analysis to to represent a multivariate data table as smaller set of variables.
    :param df: preprocessed dataframe from preprocessing_ohe
    :return: a new dataframe which has reduced number of dimensions  
 
    """
    # Apply dimensionality reduction
    pca = PCA(n_components=2)
    feature_table_reduced = pca.fit_transform(df)
    
    return feature_table_reduced

# df of review with feature table after dimensionality reduction
feature_table_reduced_review=pca(df_pre_review)

# df with receipt feature table after dimensionality reduction
feature_table_reduced_receipt=pca(df_pre_receipt)