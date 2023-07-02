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
|--|--anomaly_detection                 : Anomaly detection using Isolation Forest 
|--|--|--preprocessing_ohe.py           : Preprocessing data with one-hot encoding  
|--|--|--dimensionality_reduction.py    : Reducing dimension using PCA  
|--|--|--isolation_forests.py           : Finding anomalies with IsolationForest  
|--|--|--oneclass_svm.py                : Finding anomlaies using OneClassSVM  
|--|--data_integration                  : Folder for retrieve necessary data   
|--|--|--celonis_data_integration.py    : Functions for connecting to Celonis platform  
|--|--|--get_data.py                    : Retrieve data from Celonis data pool  
|--|--resource_based                    : Folder including all resource-based analysis functions  
|--|--|--batch_identification.py        : identification of resource batch  
|--|--|--find_deviations_analysis.py    : Resource-based patterns(deviations in the work pattern)  
|--|--|--find_high_rework_resources_analysis.py    :  Resource-based patterns(activities repeated by different resources)  
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
|--|--|--anomaly_detection_unittest.py
|--requirements.txt                     : Required library used in this framework  
|--.config.yaml                         : Celonis connection information  
|--Dockerfile                           : Docker image build configuration  
|--README.md                            : Intro to the project  
|--docker-compose.yml                   : Docker compose file  
|--Functional Model                     : Functional model used in RE
|--app.py                               : The flask file  
|--run_resource_based.py                : The resource-based component to be called in app.py  
|--run_tp_dc.py                         : The temporal profile and declarative constrains components to be called in app.py  

## How to Run the Project

After executing it, input the table name: reviewing 

```python
python app.py

```
