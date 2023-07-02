import pandas as pd
import pycelonis
import yaml
from pycelonis.pql import PQL, PQLColumn, PQLFilter, OrderByColumn
from pycelonis_core.utils.errors import PyCelonisNotFoundError
import numpy as np
from collections import defaultdict
from src.data_integration.celonis_data_integration import get_connection, get_celonis_info, create_pool_and_model, check_invalid_table_in_celonis, execute_PQL_query
from src.data_integration.get_data import get_execution_time_per_res_per_act, get_unique_activity, get_unique_resource, get_res_act_relation, get_target_activity_with_start_end_timestamp 
from src.resource_based.resource_performance import resource_performance
from src.resource_based.batch_identification import batch_identification
from src.data_integration.get_data import get_caseid_activity_lifecycle_resource, trace_cluster, split_df
from src.resource_based.find_high_rework_resources_analysis import find_high_rework_resources
from src.resource_based.find_deviations_analysis import find_deviations
from run_tp_dc import get_variants_info, get_standard_behavior, temporal_profile_analysis, temporal_profile_deviations, declarative_constraint_analysis
from src.declarative_constraints.constraint_operations import CONSTRAINT_LIBRARY
from flask import Flask, render_template_string, request
import math
from run_resource_based import resource_based_overall


table_name = input("Please enter table name: ")

celonis = get_connection()
le, me, df_sim, df_seq, df_con, high_rework_resources, deviations = resource_based_overall(celonis, table_name)
data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name, lifecycle = get_celonis_info(celonis=celonis)

trace_with_counts = trace_cluster(data_model, table_name, case_column_name, act_column_name, res_column_name, lifecycle)
first_p, first_p_id, rest, rest_id = split_df(trace_with_counts)


variants_info = get_variants_info(data_model, table_name, case_column_name, act_column_name, res_column_name,lifecycle)

main, main_id, new, new_id = get_standard_behavior(variants_info,0.2)


temporal_profile_task_dur_all, all_task_dur, temporal_profile_time_dis_all, all_time_dis, temporal_profile_task_dur_main, main_task_dur, temporal_profile_dis_main, main_dis, temporal_profile_task_dur_new, new_task_dur, temporal_profile_time_dis_new, new_time_dis = temporal_profile_analysis(data_pool, data_model, table_name, case_column_name, act_column_name, time_column_name, lifecycle,main_id)


normal_dur, anomaly_dur, normal_dis, anomaly_dis=temporal_profile_deviations(new_task_dur, new_time_dis,temporal_profile_task_dur_main,temporal_profile_dis_main, 0.1)


constraints_extracted=declarative_constraint_analysis(data_model, table_name, act_column_name, list(CONSTRAINT_LIBRARY.keys()), CONSTRAINT_LIBRARY,
                                    variants_info, percentage_of_instances=0.5)



app = Flask(__name__)



@app.route('/')
def home():

    template = '''
    <html>
        <body>
            <h1>Automatic Conformance Checking insights in Celonis</h1>
            <ul>
                <li><a href="/standard_behaviour">standard behaviour</a></li>
                <li><a href="/resource-based_analysis">resource-based analysis</a></li>
                <li><a href="/anomaly_detection">anomaly detection</a></li>
                <li><a href="/temporal_profile_analysis">temporal profile analysis</a></li>
                <li><a href="/declarative_constraints">declarative constraints</a></li>
                
            </ul>
        </body>
    </html>
    '''
    return render_template_string(template)


@app.route('/standard_behaviour')
def route1():
 

    df = pd.DataFrame(first_p, columns=['standard_behaviour'])  
    result = df.to_html()
    template = '''
    <html>
        <body>
            <h1>standard behaviour</h1>
            {{result | safe}}
            <p><a href="/">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template, result=result)



@app.route('/resource-based_analysis')
def resource_based_analysis():
    template = '''
    <html>
        <body>
            <h1>Resource-based Analysis</h1>
            <ul>
                <li><a href="/resource_performance">resource performance (least/most efficient)</a></li>
                <li><a href="/work_pattern_deviation">work pattern deviation</a></li>
                <li><a href="/activities_repeated_by_different_resources">activities repeated by different resources</a></li>
                <li><a href="/batch_identification">identification of resource batch</a></li>
            </ul>
        </body>
    </html>
    '''
    return render_template_string(template)

@app.route('/resource_performance')
def route2():
 
    result1 = me.to_html()
    result2 = le.to_html()
    
    template = '''
    <html>
        <body>
            <h1>Resource-activity performance</h1>
            <h2>most efficient resources</h2>
            {{result1 | safe}}
            <h2>least efficient resources</h2>
            {{result2 | safe}}
            <p><a href="/">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template, result1=result1, result2=result2)


@app.route('/work_pattern_deviation')
def route22():
 
    result = deviations.to_html()
    template = '''
    <html>
        <body>
            <h1>work pattern deviation</h1>
            {{result | safe}}
            <p><a href="/">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template, result=result)

@app.route('/activities_repeated_by_different_resources')
def route23():
 
    df = pd.DataFrame(high_rework_resources, columns=['high_rework_resources'])  
    result = df.to_html()
    template = '''
    <html>
        <body>
            <h1>activities repeated by different resources</h1>
            {{result | safe}}
            <p><a href="/">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template, result=result)




@app.route('/batch_identification')
def route24():
    result1 = df_sim.to_html()
    result2 = df_seq.to_html()
    result3 = df_con.to_html()
    
    template = '''
    <html>
        <body>
            <h1>Batch Identification</h1>
            <h2>Simultaneous</h2>
            {{result1 | safe}}
            <h2>Sequential</h2>
            {{result2 | safe}}
            <h2>Concurrent</h2>
            {{result3 | safe}}
            <p><a href="/">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template, result1=result1, result2=result2, result3=result3)

@app.route('/temporal_profile_analysis')
def route3():
    
    normal_dur_df = pd.DataFrame([nd.to_dict() for nd in normal_dur])
    anomaly_dur_df = pd.DataFrame([ad.to_dict() for ad in anomaly_dur])
    normal_dis_df = pd.DataFrame([nd.to_dict() for nd in normal_dis])
    anomaly_dis_df = pd.DataFrame([ad.to_dict() for ad in anomaly_dis])

    result1 = normal_dur_df.to_html()
    result2 = anomaly_dur_df.to_html()
    result3 = normal_dis_df.to_html()
    result4 = anomaly_dis_df.to_html()

    template = '''
    <html>
        <body>
            <h1>temporal profile analysis</h1>
            <h2>Normal durations</h2>
            {{result1 | safe}}
            <h2>Anomaly durations</h2>
            {{result2 | safe}}
            <h2>Normal distances</h2>
            {{result3 | safe}}
            <h2>Anomaly distances</h2>
            {{result4 | safe}}
            <p><a href="/">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template, result1=result1, result2=result2, result3=result3, result4=result4)

@app.route('/declarative_constraints')
def route4():
 
    df = pd.DataFrame(constraints_extracted, columns=['constraints_extracted'])  
    result = df.to_html()
    template = '''
    <html>
        <body>
            <h1>The extracted constraints</h1>
            {{result | safe}}
            <p><a href="/">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template, result=result)


if __name__ == '__main__':
    app.run()
