# Group4-Automatic-Conformance-Checking-insights-in-Celonis
## Docker Set-up
Build docker image  
`docker build -t .Dockerfile`   
Run your docker  
`docker-compose up`  
After doing this you will get all the necessary packages installed

## File Structure
Home

|--src                              : Source-Code folder  
|--|--resource_based                : Folder including all resource-based analysis functions  
|--|--temporal_profile              : Folder including all temporal-based analysis functions  
|--test                             : Test folder  
|--|--test_input_data               : Folder including some test event logs  
|--|--|--receipt.csv  
|--|--|--receipt.xes  
|--|--|--reviewing.csv  
|--|--|--reviewing.xes  
|--|--test_notebooks                 : Folder for jupyter notebooks including some small test examples  
|--|--|--test_resource_based.ipynb  
|--|--unit_test                     : Folder including unit tests  
|--|--|--resource_based_unit_test.py    : Python filer that includes some unit test for resource-based analysis functions  
|--requirements.txt             : Required library used in this framework  
|--.config.yaml                  : Celonis connection information  
|--Dockerfile                   : Docker image build configuration  
|--README.md                    : Intro to the project  
|--docker-compose.yml           : Docker compose file  
|--Functional Model             : Functional model used in RE

## Usage

Connect with Celonis platform, get data pool and data model, and check invalidity of table
```python
from src.celonis_data_integration import get_connection, get_celonis_info, check_invalid_table_in_celonis
from src.get_data import get_execution_time_per_res_per_act
from src.resource_based_analysis import resource_performance

# connect to Celonis
celonis = get_connection()

# get the data pool and data model of our project
data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name = get_celonis_info(celonis=celonis)

# check if one table is invalid (does not exist in our data pool/model)
flag = check_invalid_table_in_celonis(celonis, table="receipt")

# One example of getting data of table receipt from our data pool
if not flag:
    df = get_execution_time_per_res_per_act(data_model, "receipt", case_column_name, act_column_name, res_column_name, time_column_name)
    
# One example: get the least and the most efficient resource of above data
least, most = resource_performance(df)

```
