import pandas as pd
from src.data_integration.celonis_data_integration import get_connection, get_celonis_info, \
    check_invalid_table_in_celonis
from src.data_integration.get_data import trace_cluster, split_df, calculate_temporal_profile_task_duration, \
    calculate_temporal_profile_temporal_distance, get_execution_time_per_res_per_act, \
    get_caseid_activity_lifecycle_resource, get_target_activity_with_start_end_timestamp, get_unique_resource, \
    get_unique_activity
from run_tp_dc import get_variants_info, get_standard_behavior, temporal_profile_deviations, \
    declarative_constraint_analysis, anomaly_detection, anomaly_tables
from src.declarative_constraints.constraint_operations import CONSTRAINT_LIBRARY
from flask import Flask, render_template_string, send_file, request, redirect, url_for
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from src.resource_based.batch_identification import batch_identification
from src.resource_based.find_deviations_analysis import find_deviations
from src.resource_based.find_high_rework_resources_analysis import find_high_rework_resources
from src.resource_based.resource_performance import resource_performance

TABLE_NAME = None
CELONIS = None
DATA_POOL = None
POOL_NAME = None
DATA_MODEL = None
MODEL_NAME = None
CASE_COLUMN_NAME = None
ACT_COLUMN_NAME = None
TIME_COLUMN_NAME = None
RES_COLUMN_NAME = None
LIFECYCLE = None
DF_ANOMALY = None
PRE_ANOMALY = None
app = Flask(__name__)

df_r = None

pre, pca_table, a_if, ar_if, a_svm, ar_svm = None, None, None, None, None, None


@app.route('/', methods=["POST", "GET"])
def home():
    template = '''
            <html>
            <head>
            <title>Home</title>
            <h1>Welcome to Automatic Conformance Checking insights in Celonis</h1>
            <style>
                .container {
                    text-align: center;
                    margin-top: 100px;
                }
            </style>
            </head>
            <body>
            <div class="container">
                <form action="" method='post' style="">
                <input type="text" name="table_name">
                <br><br><input type=submit value='Submit Table' name="submit_table">
                <br><br><input type=submit value='Change Account Settings' name="setting">
                <br><br>Status:{{ message }}
            </div>
            </body>
            </html>'''

    global CELONIS
    global DATA_POOL, POOL_NAME, DATA_MODEL, MODEL_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME, TIME_COLUMN_NAME, RES_COLUMN_NAME, LIFECYCLE
    global df_r
    global pre, pca_table, a_if, ar_if, a_svm, ar_svm
    # refresh
    df_r = None
    pre, pca_table, a_if, ar_if, a_svm, ar_svm = None, None, None, None, None, None

    url_login = url_for('login')
    print(url_login)
    url_content = url_for('content')
    print(url_content)
    if request.method == 'GET':
        CELONIS = get_connection()
        print(isinstance(CELONIS, str))
        if isinstance(CELONIS, str):
            return render_template_string(template,
                                          message=CELONIS + " Please click the button Change Account Settings to login!")
        print(get_celonis_info(CELONIS))
        if not isinstance(get_celonis_info(CELONIS), str):
            DATA_POOL, DATA_MODEL, POOL_NAME, MODEL_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME, TIME_COLUMN_NAME, RES_COLUMN_NAME, LIFECYCLE = get_celonis_info(
                CELONIS)
            return render_template_string(template,
                                          message='You have logged in Celonis! Please enter the event log name!')
        else:
            return render_template_string(template,
                                          message="Invalid account configuration! Please click the button Change Account Settings to login!")
    if request.method == 'POST':
        bt_a = request.values.get("submit_table")
        print(bt_a)
        bt_b = request.values.get("setting")
        print(bt_b)
        if bt_a == 'Submit Table':
            print("got table name")
            global TABLE_NAME
            TABLE_NAME = request.form.get('table_name')
            print(TABLE_NAME)

            if DATA_MODEL is not None and TABLE_NAME is not None:
                if not check_invalid_table_in_celonis(DATA_MODEL, TABLE_NAME):
                    return redirect(url_content)
                else:
                    TABLE_NAME = None
                    return render_template_string(template,
                                                  message="No such table in your data model, please enter an available one!")
            else:
                if DATA_MODEL is None:
                    return render_template_string(template,
                                                  message="Invalid account configuration! Please click the button Change Account Settings to login!")
                else:
                    return render_template_string(template,
                                                  message="No such table in your data model, please enter an available one!")
        if bt_b == 'Change Account Settings':
            print(redirect(url_login))
            return redirect(url_login)
        return render_template_string(template,
                                      message='You have logged in Celonis! Please enter the event log name!')


@app.route('/login', methods=['POST', 'GET'])
def login():
    template = '''
    <html lang="en">  
        <head>  
         <meta charset="UTF-8">  
         <title>Login</title> 
        </head>  
        <body>  
         <div id="login">  
             <h1>Login</h1>  
             <form method="post">
                 <br><br>Celonis URL* <input type="text"  placeholder="Celonis URL" name="url" >
                 <br><br>API Token*<input  type="text" placeholder="API Token" name="api_key" >
                 <br><br>Data Pool Name* <input  type="text" placeholder="Data Pool Name" name="data_pool" >
                 <br><br>Dat Model Name* <input  type="text" placeholder="Data Model Name" name="data_model" >
                 <br><br>case_column_name <input  type="text" placeholder="case:concept:name" name="case_column_name" >
                 <br><br>activity_column_name <input  type="text" placeholder="concept:name" name="activity_column_name" >
                 <br><br>timestamp_column_name <input  type="text" placeholder={timestamp_column_name} name="timestamp_column_name" >
                 <br><br>resource_column_name <input  type="text" placeholder="org:resource" name="resource_column_name" >
                 <br><br>lifecycle_column_name <input  type="text" placeholder="lifecycle:transition" name="lifecycle_column_name" >
                 <br><br>*Must have
                 <br><br><input  type="submit" value="Login" name="Login">
                 <br><br><input  type="submit" value="Back" name="Back">
                 {{msg}}
             </form>  
         </div>  
        </body>  
    </html>
    '''
    if request.method == "GET":
        return render_template_string(template)
    if request.method == "POST":
        bt = request.values.get("Login")
        bt_back = request.values.get("Back")
        if bt == "Login":
            if request.form.get("url") == "" or request.form.get("api_key") == "" or request.form.get(
                    "data_pool") == "" or request.form.get("data_model") == "":
                return render_template_string(template, msg="Please fill all the block with *!")
            case_column_name = request.form['case_column_name']
            activity_column_name = request.form['activity_column_name']
            timestamp_column_name = request.form['timestamp_column_name']
            res_column_name = request.form['resource_column_name']
            lifecycle = request.form['lifecycle_column_name']
            if request.form['case_column_name'] == "":
                case_column_name = "case:concept:name"
            if request.form['activity_column_name'] == "":
                activity_column_name = "concept:name"
            if request.form['timestamp_column_name'] == "":
                timestamp_column_name = "time:timestamp"
            if request.form['resource_column_name'] == "":
                res_column_name = "org:resource"
            if request.form['lifecycle_column_name'] == "":
                lifecycle = "lifecycle:transition"

            settings = """case_column_name: {case_column_name}
activity_column_name: {activity_column_name}
timestamp_column_name: {timestamp_column_name}
resource_column_name: {resource_column_name}
lifecycle_column_name: {lifecycle_column_name}
data_model: {data_model}
data_pool: {data_pool}
data_job:{data_job}
celonis:
    {{  base_url : {url}, 
        api_token : {api_token}}}
            """.format(url=request.form['url'],
                       api_token=request.form['api_key'],
                       data_pool=request.form['data_pool'],
                       data_model=request.form['data_model'],
                       data_job="",
                       case_column_name=case_column_name,
                       activity_column_name=activity_column_name,
                       timestamp_column_name=timestamp_column_name,
                       resource_column_name=res_column_name,
                       lifecycle_column_name=lifecycle)
            f = open(".config.yaml", "w")
            f.write(settings)
            f.close()
            return redirect("/")
        if bt_back == "Back":
            return redirect("/")


@app.route('/content')
def content():
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
            <p><a href="/">Back</a></p>
            </body>
        </html>
        '''
    return render_template_string(template)


@app.route('/standard_behaviour', methods=["GET", "POST"])
def route1():
    first_threshold = 0.2
    trace_with_counts = trace_cluster(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME, RES_COLUMN_NAME,
                                      LIFECYCLE)
    first_p, first_p_id, rest, rest_id = split_df(trace_with_counts, first_threshold)
    df = pd.DataFrame(first_p, columns=['standard_behaviour'])
    result = df.to_html()
    template = '''
    <html>
        <body>
            <h1>standard behaviour</h1>
                <div class="container">
                        <form action="" method='post' style="">
                        Threshold (0, 1] <input type=text name="standard"> 
                        <br><br><input type=submit value='SUBMIT' name="submit_standard">
                        Status : {{ message }}
                    </div>
            {{result | safe}}
            <p><a href="/content">Back</a></p>
        </body>
    </html>
    '''
    if request.method == "POST":
        bt = request.values.get("submit_standard")
        if bt == "SUBMIT":
            print(request.form.get("standard"))
            if request.form.get("standard") == "":
                return render_template_string(template, result=result,
                                              message=f"Empty Value!")
            first_threshold_new = float(request.form.get("standard"))
            if 0 < first_threshold_new <= 1:
                first_p, first_p_id, rest, rest_id = split_df(trace_with_counts, first_threshold_new)
                df = pd.DataFrame(first_p, columns=['standard_behaviour'])
                result = df.to_html()
                return render_template_string(template, result=result,
                                              message=f"Threshold is set to {first_threshold_new}")
            else:
                return render_template_string(template, result=result,
                                              message=f"{first_threshold_new} is invalid. Please choose a proper value in (0, 1]")
    return render_template_string(template, result=result, message=f"Threshold is set to {first_threshold}")


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
            <p><a href="/content">Back</a></p>
        </body>
    </html>
    '''
    return render_template_string(template)


@app.route('/resource_performance')
def route2():
    df = get_execution_time_per_res_per_act(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME, RES_COLUMN_NAME,
                                            TIME_COLUMN_NAME)
    le, me = resource_performance(df)
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


@app.route('/work_pattern_deviation', methods=["GET", "POST"])
def route22():
    template = '''
        <html>
            <body>
                <div class="container">
                    <form action="" method='post' style="">
                    Threshold: frequency of activity executed by one resource <input type=text name="frequency">
                    <input type=submit value='SUBMIT' name="submit_frequency">
                    Status : {{ message }}
                </div>
                <h1>work pattern deviation</h1>
                {{result | safe}}
                <p><a href="/resource-based_analysis">Back</a></p>
            </body>
        </html>
        '''
    threshold = 1
    df = get_caseid_activity_lifecycle_resource(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME,
                                                RES_COLUMN_NAME,  LIFECYCLE)

    deviations = find_deviations(df, threshold=threshold)
    result = deviations.to_html()
    if request.method == "POST":
        if request.form.get("frequency") == "":
            return render_template_string(template, result=result, message=f"Empty Value!")
        bt = request.values.get("submit_frequency")
        if bt == "SUBMIT":
            threshold_new = int(request.form.get("frequency"))
            if threshold_new < 1:
                return render_template_string(template, result=result, message=f"Invalid Value!")
            df = get_caseid_activity_lifecycle_resource(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME,
                                                        RES_COLUMN_NAME, LIFECYCLE)

            deviations = find_deviations(df, threshold=threshold_new)
            result = deviations.to_html()
            return render_template_string(template, result=result, message=f"Threshold is set to {threshold_new}")

    return render_template_string(template, result=result, message=f"Threshold is set to {threshold}")


@app.route('/activities_repeated_by_different_resources', methods=["GET", "POST"])
def route23():
    template = '''
        <html>
            <body>
                <h1>activities repeated by different resources</h1>
                <div class="container">
                        <form action="" method='post' style="">
                        Threshold: one activity should be executed less or equal to <input type=text name="act"> resources
                        <br><br><input type=submit value='SUBMIT' name="submit_act">
                        Status : {{ message }}
                    </div>
                {{result | safe}}
                <p><a href="/resource-based_analysis">Back</a></p>
            </body>
        </html>
        '''
    count_threshold = 2
    df = get_caseid_activity_lifecycle_resource(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME,
                                                RES_COLUMN_NAME,
                                                LIFECYCLE)

    # find high rework resources
    high_rework_resources = find_high_rework_resources(df, rework_threshold=1, count_threshold=count_threshold)
    df_res = pd.DataFrame(high_rework_resources, columns=['high_rework_resources'])
    result = df_res.to_html()

    if request.method == "POST":
        bt = request.values.get("submit_act")
        if bt == "SUBMIT":
            if request.form.get("act") == "":
                return render_template_string(template, result=result, message=f"Invalid!")
            count_threshold_new = int(request.form.get("act"))
            if count_threshold_new < 1:
                return render_template_string(template, result=result, message=f"Invalid Value!")

            high_rework_resources = find_high_rework_resources(df, rework_threshold=1, count_threshold=count_threshold_new)
            df_res = pd.DataFrame(high_rework_resources, columns=['high_rework_resources'])
            result = df_res.to_html()

            return render_template_string(template, result=result, message=f"Threshold is set to {count_threshold_new}")

    return render_template_string(template, result=result, message=f"Threshold is set to {count_threshold}")


@app.route('/batch_identification')
def route24():
    batch_data = get_target_activity_with_start_end_timestamp(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME,
                                                              RES_COLUMN_NAME, TIME_COLUMN_NAME)
    resources = get_unique_resource(batch_data, "resource")
    activities = get_unique_activity(batch_data, "activity")

    import warnings
    warnings.filterwarnings('ignore')

    df_sim, df_seq, df_con = batch_identification(batch_data, activities)
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
                <p><a href="/content">Back</a></p>
            </body>
        </html>
        '''

    return render_template_string(template)


@app.route('/Task_Duration_and_Temporal_Distance')
def route_task_duration_overall():
    temporal_profile_task_dur_all, all_task_dur = calculate_temporal_profile_task_duration(DATA_MODEL, TABLE_NAME,
                                                                                           "overall",
                                                                                           case_column=CASE_COLUMN_NAME,
                                                                                           activity_column=ACT_COLUMN_NAME,
                                                                                           time_column=TIME_COLUMN_NAME,
                                                                                           lifecycle_column=LIFECYCLE)
    temporal_profile_time_dis_all, all_time_dis = calculate_temporal_profile_temporal_distance(DATA_MODEL, TABLE_NAME,
                                                                                               "overall",
                                                                                               case_column=CASE_COLUMN_NAME,
                                                                                               activity_column=ACT_COLUMN_NAME,
                                                                                               time_column=TIME_COLUMN_NAME,
                                                                                               lifecycle_column=LIFECYCLE)

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


@app.route('/Anomalies', methods=["GET", "POST"])
def route3():
    template = '''
        <html>
            <body>
                <h1>Anomalies in temporal profile analysis</h1>
                <div class="container">
                    <form action="" method='post' style="">
                    z-score threshold: <input type=text name="z_t">
                    <input type=submit value='SUBMIT' name="submit_z_t">
                    Status:{{ message }}
                </div>
                <br><br>
                <h2>Task duration: normal case</h2>
                {{result1 | safe}}
                <h2>Task duration: anomaly case</h2>
                {{result2 | safe}}
                <h2>Temporal distance: normal case</h2>
                {{result3 | safe}}
                <h2>Temporal distance: anomaly case</h2>
                {{result4 | safe}}
                <p><a href="/temporal_profile_analysis">Back</a></p>
            </body>
        </html>
        '''
    z_threshold = 3
    variants_info = get_variants_info(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME, RES_COLUMN_NAME,
                                      LIFECYCLE)

    main, main_id, new, new_id = get_standard_behavior(variants_info, 0.2)
    temporal_profile_task_dur_main, main_task_dur = calculate_temporal_profile_task_duration(DATA_MODEL, TABLE_NAME,
                                                                                             "mainstream",
                                                                                             case_column=CASE_COLUMN_NAME,
                                                                                             activity_column=ACT_COLUMN_NAME,
                                                                                             time_column=TIME_COLUMN_NAME,
                                                                                             lifecycle_column=LIFECYCLE,
                                                                                             mainstream_case_id=main_id)

    temporal_profile_dis_main, main_dis = calculate_temporal_profile_temporal_distance(DATA_MODEL, TABLE_NAME,
                                                                                       "mainstream",
                                                                                       case_column=CASE_COLUMN_NAME,
                                                                                       activity_column=ACT_COLUMN_NAME,
                                                                                       time_column=TIME_COLUMN_NAME,
                                                                                       lifecycle_column=LIFECYCLE,
                                                                                       mainstream_case_id=main_id)

    temporal_profile_task_dur_new, new_task_dur = calculate_temporal_profile_task_duration(DATA_MODEL, TABLE_NAME,
                                                                                           "new",
                                                                                           case_column=CASE_COLUMN_NAME,
                                                                                           activity_column=ACT_COLUMN_NAME,
                                                                                           time_column=TIME_COLUMN_NAME,
                                                                                           lifecycle_column=LIFECYCLE,
                                                                                           mainstream_case_id=main_id)

    temporal_profile_time_dis_new, new_time_dis = calculate_temporal_profile_temporal_distance(DATA_MODEL, TABLE_NAME,
                                                                                               "new",
                                                                                               case_column=CASE_COLUMN_NAME,
                                                                                               activity_column=ACT_COLUMN_NAME,
                                                                                               time_column=TIME_COLUMN_NAME,
                                                                                               lifecycle_column=LIFECYCLE,
                                                                                               mainstream_case_id=main_id)

    normal_dur, anomaly_dur, normal_dis, anomaly_dis = temporal_profile_deviations(new_task_dur, new_time_dis,
                                                                                   temporal_profile_task_dur_main,
                                                                                   temporal_profile_dis_main,
                                                                                   z_threshold)

    normal_dur_df = pd.DataFrame([nd.to_dict() for nd in normal_dur])
    anomaly_dur_df = pd.DataFrame([ad.to_dict() for ad in anomaly_dur])
    normal_dis_df = pd.DataFrame([nd.to_dict() for nd in normal_dis])
    anomaly_dis_df = pd.DataFrame([ad.to_dict() for ad in anomaly_dis])

    result1 = normal_dur_df.to_html()
    result2 = anomaly_dur_df.to_html()
    result3 = normal_dis_df.to_html()
    result4 = anomaly_dis_df.to_html()

    if request.method == "POST":
        bt = request.values.get("submit_z_t")
        if bt == "SUBMIT":
            if request.form.get("z_t") == "":
                return render_template_string(template, result1=result1, result2=result2, result3=result3,
                                              result4=result4, message=f"Invalid!")
            z_threshold_new = float(request.form.get("z_t"))
            normal_dur, anomaly_dur, normal_dis, anomaly_dis = temporal_profile_deviations(new_task_dur, new_time_dis,
                                                                                           temporal_profile_task_dur_main,
                                                                                           temporal_profile_dis_main,
                                                                                           z_threshold_new)

            normal_dur_df = pd.DataFrame([nd.to_dict() for nd in normal_dur])
            anomaly_dur_df = pd.DataFrame([ad.to_dict() for ad in anomaly_dur])
            normal_dis_df = pd.DataFrame([nd.to_dict() for nd in normal_dis])
            anomaly_dis_df = pd.DataFrame([ad.to_dict() for ad in anomaly_dis])

            result1 = normal_dur_df.to_html()
            result2 = anomaly_dur_df.to_html()
            result3 = normal_dis_df.to_html()
            result4 = anomaly_dis_df.to_html()
            return render_template_string(template, result1=result1, result2=result2, result3=result3, result4=result4,
                                          message=f"z_score threshold is set to {z_threshold_new}")

    return render_template_string(template, result1=result1, result2=result2, result3=result3, result4=result4, message=f"z_score threshold is set to {z_threshold}")


@app.route('/declarative_constraints', methods=["GET", "POST"])
def route4():
    template = '''
        <html>
            <body>
                <h1>The extracted constraints</h1>
                <div class="container">
                    <form action="" method='post' style="">
                    Percentage of Instance [0, 1]: <input type=text name="poi">
                    <input type=submit value='SUBMIT' name="submit_poi">
                    Status:{{ message }}
                </div>
                <br><br>
                {{result | safe}}
                <p><a href="/content">Back</a></p>
            </body>
        </html>
        '''
    poi = 0.8
    variants_info = get_variants_info(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME, RES_COLUMN_NAME,
                                      LIFECYCLE)
    constraints_extracted = declarative_constraint_analysis(DATA_MODEL, TABLE_NAME, ACT_COLUMN_NAME,
                                                            list(CONSTRAINT_LIBRARY.keys()), CONSTRAINT_LIBRARY,
                                                            variants_info, poi)
    df = pd.DataFrame(constraints_extracted, columns=['constraints_extracted'])
    result = df.to_html()

    if request.method == "POST":
        bt = request.values.get("submit_poi")
        if bt == "SUBMIT":
            if request.form.get("poi") == "":
                return render_template_string(template, result=result,
                                              message=f"Invalid. Please choose a proper value in [0, 1]")
            poi_new = float(request.form.get("poi"))

            if 0 <= poi_new <= 1:
                constraints_extracted = declarative_constraint_analysis(DATA_MODEL, TABLE_NAME, ACT_COLUMN_NAME,
                                                                        list(CONSTRAINT_LIBRARY.keys()),
                                                                        CONSTRAINT_LIBRARY,
                                                                        variants_info, poi_new)
                df = pd.DataFrame(constraints_extracted, columns=['constraints_extracted'])
                result = df.to_html()
                return render_template_string(template, result=result,
                                              message=f"Percentage of Instances is set to {poi_new}")
            else:
                return render_template_string(template, result=result,
                                              message=f"{poi_new} is invalid. Please choose a proper value in [0, 1]")
    return render_template_string(template, result=result, message=f"Percentage of Instances is set to {poi}")


@app.route('/anomaly_detection')
def route5():
    global df_r
    global pre, pca_table, a_if, ar_if, a_svm, ar_svm
    if df_r is None or pre is None or pca_table is None or a_if is None or ar_if is None or a_svm is None or ar_svm is None:
        df_r = anomaly_detection(DATA_MODEL, TABLE_NAME, CASE_COLUMN_NAME, ACT_COLUMN_NAME, RES_COLUMN_NAME,
                                 TIME_COLUMN_NAME)
        pre, pca_table, a_if, ar_if, a_svm, ar_svm = anomaly_tables(TABLE_NAME, df_r)
    template = '''
    <html>
        <body>
            <h1>Anomaly Detection</h1>
            <ul>
                <li><a href="/plot">plot</a></li>
                <li><a href="/table">table</a></li>
            </ul>
            <p><a href="/content">Back</a></p>
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
    plt.show()
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
    plt.show()
    img = BytesIO()
    plt.savefig(img, format='png', dpi=200)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/table')
def route52():
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
    if ar_if is not None and ar_svm is not None:
        result1 = ar_if.to_html()
        result2 = ar_svm.to_html()

    elif ar_if is not None and ar_svm is None:
        result1 = ar_if.to_html()
        result2 = f"{TABLE_NAME} is not valid for here."
    else:
        result1 = f"{TABLE_NAME} is not valid for here."
        result2 = ar_svm.to_html()

    return render_template_string(template, result1=result1, result2=result2)


if __name__ == '__main__':
    print('start')
    app.run(host='0.0.0.0')
