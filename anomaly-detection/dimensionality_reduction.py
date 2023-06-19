from preprocessing_ohe import df_pre_receipt,df_pre_review

from sklearn.decomposition import PCA
import pandas as pd


def pca(df):
    # Apply dimensionality reduction
    pca = PCA(n_components=2)
    feature_table_reduced = pca.fit_transform(df)
    
    return feature_table_reduced

# df of review with feature table after dimensionality reduction
feature_table_reduced_review=pca(df_pre_review)

# df with receipt feature table after dimensionality reduction
feature_table_reduced_receipt=pca(df_pre_receipt)