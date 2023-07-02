# Group4-Automatic-Conformance-Checking-insights-in-Celonis
## Docker Set-up
Build docker image  
`docker build -t .Dockerfile`   
Run your docker  
`docker-compose up`  
After doing this you will get all the necessary packages installed

## Project Structure
**Home**

|--src                                  : Source-Code folder  
|--|--data_integration                  : Folder for retrieve necessary data   
|--|--|--celonis_data_integration.py    : Functions for connecting to Celonis platform  
|--|--|--get_data.py                    : Retrieve data from Celonis data pool  
|--|--resource_based                    : Folder including all resource-based analysis functions  
|--|--|--batch_identification.py        : identification of resource batch  
|--|--|--find_deviations_analysis.py    :  
|--|--|--find_high_rework_resources_analysis.py    :  
|--|--|--resource_performance.py        : the most/least efficient resource (with ranking)  
|--|--temporal_profile                  : Folder including all temporal-based analysis functions   
|--|--|--deviation_based_on_z_score.py : Calculate the z-score for non-standard behaviours based on standard-behaviour  
|--|--declarative_constraints           : Folder including all declarative analysis functions  
|--|--|--constraint_operations.py       : Constraint generation and constraint extraction  
|--|--|--templates.py                   : Regular expression for constraint templates
|--test                                 : Test folder  
|--|--test_input_data                   : Folder including some test event logs  
|--|--|--receipt.csv  
|--|--|--receipt.xes  
|--|--|--reviewing.csv  
|--|--|--reviewing.xes  
|--|--test_notebooks                    : Folder for jupyter notebooks including some small test examples  
|--|--|--test_resource_based.ipynb  
|--|--|--check_functions_with_real_data.ipynb  
|--|--unit_test                         : Folder including unit tests  
|--|--|--declarative_constraints_templates_unit_test.py  
|--|--|--declarative_constraints_operations_unit_test.py
|--|--|--resource_based_unit_test.py  
|--|--|--temporal_profile_unit_test.py
|--requirements.txt                     : Required library used in this framework  
|--.config.yaml                         : Celonis connection information  
|--Dockerfile                           : Docker image build configuration  
|--README.md                            : Intro to the project  
|--docker-compose.yml                   : Docker compose file  
|--Functional Model                     : Functional model used in RE

## How to Run the Project

Connect with Celonis platform, get data pool and data model, and check invalidity of table

```python
from src.data_integration.celonis_data_integration import get_connection, get_celonis_info, check_invalid_table_in_celonis
from src.data_integration.get_data import get_execution_time_per_res_per_act
from src.resource_based.resource_performance import resource_performance

# connect to Celonis
celonis = get_connection()

# get the data pool and data model of our project
data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name = get_celonis_info(
    celonis=celonis)

# check if one table is invalid (does not exist in our data pool/model)
flag = check_invalid_table_in_celonis(celonis, table="receipt")

# One example of getting data of table receipt from our data pool
if not flag:
    df = get_execution_time_per_res_per_act(data_model, "receipt", case_column_name, act_column_name, res_column_name,
                                            time_column_name)

# One example: get the least and the most efficient resource of above data
least, most = resource_performance(df)

```
