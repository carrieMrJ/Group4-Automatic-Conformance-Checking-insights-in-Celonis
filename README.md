# Group4-Automatic-Conformance-Checking-insights-in-Celonis
## Usage
Connect with Celonis platform, get data pool and data model, and check invalidity of table
```python
from src.celonis_data_integration import get_connection, get_celonis_info, check_invalid_table_in_celonis
# connect to Celonis
celonis = get_connection()

# get the data pool and data model of our project
data_pool, data_model， pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name = get_celonis_info(celonis=celonis)

# check if one table is invalid (does not exist in our data pool/model)
check_invalid_table_in_celonis(celonis, table="table_name")
```
