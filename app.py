import pandas as pd
from src.data_integration.celonis_data_integration import get_connection, get_celonis_info
from src.data_integration.get_data import trace_cluster, split_df
from run_tp_dc import get_variants_info, get_standard_behavior, temporal_profile_analysis, temporal_profile_deviations, \
    declarative_constraint_analysis, anomaly_detection, anomaly_tables
from src.declarative_constraints.constraint_operations import CONSTRAINT_LIBRARY
from flask import Flask, render_template_string, send_file
import matplotlib.pyplot as plt
from io import BytesIO
from run_resource_based import resource_based_overall

table_name = input("Please enter table name: ")

celonis = get_connection()
le, me, df_sim, df_seq, df_con, high_rework_resources, deviations = resource_based_overall(celonis, table_name)
data_pool, data_model, pool_name, model_name, case_column_name, act_column_name, time_column_name, res_column_name, lifecycle = get_celonis_info(
    celonis=celonis)

trace_with_counts = trace_cluster(data_model, table_name, case_column_name, act_column_name, res_column_name, lifecycle)
first_p, first_p_id, rest, rest_id = split_df(trace_with_counts)

variants_info = get_variants_info(data_model, table_name, case_column_name, act_column_name, res_column_name, lifecycle)

main, main_id, new, new_id = get_standard_behavior(variants_info, 0.2)

temporal_profile_task_dur_all, all_task_dur, temporal_profile_time_dis_all, all_time_dis, temporal_profile_task_dur_main, main_task_dur, temporal_profile_dis_main, main_dis, temporal_profile_task_dur_new, new_task_dur, temporal_profile_time_dis_new, new_time_dis = temporal_profile_analysis(
    data_model, table_name, case_column_name, act_column_name, time_column_name, lifecycle, main_id)

normal_dur, anomaly_dur, normal_dis, anomaly_dis = temporal_profile_deviations(new_task_dur, new_time_dis,
                                                                               temporal_profile_task_dur_main,
                                                                               temporal_profile_dis_main, 0.1)

constraints_extracted = declarative_constraint_analysis(data_model, table_name, act_column_name,
                                                        list(CONSTRAINT_LIBRARY.keys()), CONSTRAINT_LIBRARY,
                                                        variants_info, percentage_of_instances=0.5)

df_r = anomaly_detection(data_model, table_name, case_column_name, act_column_name, res_column_name, time_column_name)

pre, pca_table, a_if, ar_if, a_svm, ar_svm = anomaly_tables(table_name, df_r)

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
            <p><a href="/">Back</a></p>
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
            <p><a href="/resource-based_analysis">Back</a></p>
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
            <p><a href="/resource-based_analysis">Back</a></p>
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
            <p><a href="/resource-based_analysis">Back</a></p>
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
            <p><a href="/resource-based_analysis">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template, result1=result1, result2=result2, result3=result3)


@app.route('/temporal_profile_analysis')
def route_temporal_root():
    template = '''
        <html>
            <body>
                <h1>Temporal Profile Analysis</h1>
                <ul>
                    <li><a href="/Task_Duration_and_Temporal_Distance">Task Duration and Temporal Distance</a></li>
                    <li><a href="/Anomalies">Anomalies</a></li>
                </ul>
                <p><a href="/">Back</a></p>
            </body>
        </html>
        '''

    return render_template_string(template)


@app.route('/Task_Duration_and_Temporal_Distance')
def route_task_duration_overall():
    if temporal_profile_task_dur_all is not None and temporal_profile_time_dis_all is not None:
        result1 = temporal_profile_task_dur_all.to_html()
        result2 = temporal_profile_time_dis_all.to_html()
        template = '''
        <html>
            <body>
                <h1>Temporal Profile</h1>
                <h2>Task Duration</h2>
                {{result1 | safe}}
                <h2>Temporal Distance</h2>
                {{result2 | safe}}
                <p><a href="/temporal_profile_analysis">Back</a></p>
            </body>
        </html>
        '''
        return render_template_string(template, result1=result1, result2=result2)
    elif temporal_profile_task_dur_all is None and temporal_profile_time_dis_all is not None:
        result2 = temporal_profile_time_dis_all.to_html()
        template = '''
                <html>
                    <body>
                        <h1>Temporal Profile</h1>
                        <h2>Task Duration</h2>
                        {{result1 | safe}}
                        <h2>Temporal Distance</h2>
                        {{result2 | safe}}
                        <p><a href="/temporal_profile_analysis">Back</a></p>
                    </body>
                </html>
                '''
        return render_template_string(template, result1="Task duration cannot be calculated for this event log, "
                                                        "since the lifecycle of all activities are \'complete\'! Please refer to the temporal distance!",
                                      result2=result2)
    elif temporal_profile_task_dur_all is not None and temporal_profile_time_dis_all is None:
        result1 = temporal_profile_task_dur_all.to_html()
        template = '''
                    <html>
                        <body>
                            <h1>Temporal Profile</h1>
                            <h2>Task Duration</h2>
                            {{result1 | safe}}
                            <h2>Temporal Distance</h2>
                            {{result2 | safe}}
                            <p><a href="/temporal_profile_analysis">Back</a></p>
                        </body>
                    </html>
                        '''
        return render_template_string(template, result1=result1,
                                      result2="Temporal Distance cannot be calculated for this event log!")
    else:
        template = '''
                        <html>
                            <body>
                                <h1>Temporal Profile</h1>
                                {{result1 | safe}}
                                <p><a href="/temporal_profile_analysis">Back</a></p>
                            </body>
                        </html>
                        '''
        return render_template_string(template, result1="No available temporal profile for this event log!")


@app.route('/Anomalies')
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
            <p><a href="/temporal_profile_analysis">Back</a></p>
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


@app.route('/anomaly_detection')
def route5():
    template = '''
    <html>
        <body>
            <h1>Anomaly Detection</h1>
            <ul>
                <li><a href="/plot">plot</a></li>
                <li><a href="/table">table</a></li>
            </ul>
            <p><a href="/">Back</a></p>
        </body>
    </html>
    '''

    return render_template_string(template)


@app.route('/plot')
def route51():
    template = '''
    <html>
        <body>
            <h1>Plots</h1>
            <ul>
                <li><a href="/isolationplot">Isolation Forest</a></li>
                <li><a href="/svmplot">OneClassSVM</a></li>
            </ul>
            <p><a href="/anomaly_detection">Back</a></p>
        </body>
    </html>
    '''

    return render_template_string(template)


@app.route('/isolationplot')
def route511():
    plt.scatter(pca_table[:, 0], pca_table[:, 1], c='blue', label='Normal')

    plt.scatter(a_if[:, 0], a_if[:, 1], c='red', label='Anomaly')

    plt.title("Anomaly Detection with Isolation Forest and PCA")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend()

    img = BytesIO()
    plt.savefig(img, format='png', dpi=200)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/svmplot')
def route512():
    plt.scatter(pca_table[:, 0], pca_table[:, 1], c='blue', label='Normal')

    plt.scatter(a_svm[:, 0], a_svm[:, 1], c='red', label='Anomaly')

    plt.title("Anomaly Detection with One-Class SVM and PCA")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend()

    img = BytesIO()
    plt.savefig(img, format='png', dpi=200)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/table')
def route52():
    result1 = ar_if.to_html()
    result2 = ar_svm.to_html()

    template = '''
    <html>
        <body>
            <h1>Table</h1>
            <h2>Isolation Forests</h2>
            {{result1 | safe}}
            <h2>OneClassSVM</h2>
            {{result2 | safe}}
            <p><a href="/anomaly_detection">Back</a></p>
        </body>
    </html>
    '''

    return render_template_string(template, result1=result1, result2=result2)


if __name__ == '__main__':
    print('start')
    app.run()
