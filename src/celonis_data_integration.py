import pycelonis
import yaml
from pycelonis.pql import PQL, PQLColumn, PQLFilter, OrderByColumn
from pycelonis_core.utils.errors import PyCelonisNotFoundError


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

    pool_name = config["data_pool"]

    model_name = config["data_model"]

    case_column_name, act_column_name, time_column_name, res_column_name = config["case_column_name"], config[
        "activity_column_name"], \
        config["timestamp_column_name"], config["resource_column_name"]

    try:
        data_pool = celonis.data_integration.get_data_pools().find(pool_name)

    except PyCelonisNotFoundError:
        return f"Data pool: {pool_name} does not exist."

    try:
        data_model = data_pool.get_data_models().find(model_name)
    except PyCelonisNotFoundError:
        return f"Data model: {model_name} does not exist in data pool {pool_name}."

    return data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name


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


def check_invalid_table_in_celonis(data_model, table):
    """
    Check if the given table not in the data pool/model
    :param celonis: the connection
    :param table: table name
    :return: Return False if the table exists (valid table) otherwise retunr the error message
    """
    try:
        data_model.get_tables().find(table)
    except PyCelonisNotFoundError:
        return f"Table: \"{table}\" does not exist in data model"

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
