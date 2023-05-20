import pycelonis
import yaml
from pycelonis.pql import PQL, PQLColumn, PQLFilter, OrderByColumn
from pycelonis_core.utils.errors import PyCelonisNotFoundError

DATA_MODEL = None
MODEL_NAME = None
DATA_POOL = None
POOL_NAME = None
CASE_COLUMN = None
ACT_COLUMN = None
TIME_COLUMN = None
RES_COLUMN = None


def get_connection():
    """
    Connect to the Celonis platform
    :return: Celonis object
    """
    try:
        file = open("../.config.yaml")
        config = yaml.safe_load(file)
    except FileNotFoundError:
        return "The configuration file is empty."
    celonis_url = config["celonis"]["base_url"]
    celonis_api_token = config["celonis"]["api_token"]

    try:
        celonis = pycelonis.get_celonis(base_url=celonis_url, api_token=celonis_api_token,
                                        key_type="APP_KEY", permissions=False)
    except:
        return f"The base_url {celonis_url} or the api token {celonis_api_token} is invalid."

    return celonis


def get_celonis_info(celonis):
    """
    Get the settings of Celonis
    :param celonis: conncted celonis object
    :return: data model and data pool of our project
    """
    try:
        file = open("../.config.yaml")
        config = yaml.safe_load(file)
    except FileNotFoundError:
        return "The configuration file is empty."

    global POOL_NAME
    POOL_NAME = config["data_pool"]

    global MODEL_NAME
    MODEL_NAME = config["data_model"]

    global CASE_COLUMN, ACT_COLUMN, RES_COLUMN, TIME_COLUMN
    CASE_COLUMN, ACT_COLUMN, TIME_COLUMN, RES_COLUMN = config["case_column_name"], config["activity_column_name"], \
        config["timestamp_column_name"], config["resource_column_name"]

    try:
        data_pool = celonis.data_integration.get_data_pools().find(POOL_NAME)

    except PyCelonisNotFoundError:
        return f"Data pool: {POOL_NAME} does not exist."

    global DATA_POOL
    DATA_POOL = data_pool

    try:
        data_model = data_pool.get_data_models().find(MODEL_NAME)
    except PyCelonisNotFoundError:
        return f"Data model: {MODEL_NAME} does not exist in data pool {POOL_NAME}."

    global DATA_MODEL
    DATA_MODEL = data_model

    return data_pool, data_model


def create_pool_and_model(celonis, pool_name, model_name):
    """
    Create a data pool and a data model using the given names
    :param celonis: connected celonis object
    :param pool_name: name of the data pool
    :param model_name: name of the data model
    :return: created data model and data pool
    """
    data_pool = celonis.data_integration.create_data_pool(pool_name)
    data_model = data_pool.create_data_model(model_name)
    return data_pool, data_model


def check_invalid_table_in_celonis(celonis, table):
    """
    Check if the given table not in the data pool/model
    :param celonis: the connection
    :param table: table name
    :return: Return False if the table exists (valid table) otherwise retunr the error message
    """
    get_celonis_info(celonis)
    try:
        DATA_MODEL.get_tables().find(table)
    except PyCelonisNotFoundError:
        return f"Table: {table} does not exist in data model {MODEL_NAME}"

    return False


def execute_PQL_query(data_model, columns=None, filters=None, order_by_columns=None, distinct=False, limit=None,
                      offset=None):
    """
    Get dataframe executing PQL query
    :param data_model:
    :param columns: list of PQLColumn
    :param filters: list of PQLFilter
    :param order_by_columns: list of OrderByColumnOrderByColumn
    :param distinct: True/False
    :param limit: limit parameter
    :param offset: offfset parameter
    :return: dataframe with the result of the query
    """
    query = PQL(distinct=distinct, limit=limit, offset=offset)
    if columns:
        for c in columns:
            query += c
    if filters:
        for f in filters:
            query += f
    if order_by_columns:
        for o in order_by_columns:
            query += o

    res_df = data_model.export_data_frame(query)
    return res_df

