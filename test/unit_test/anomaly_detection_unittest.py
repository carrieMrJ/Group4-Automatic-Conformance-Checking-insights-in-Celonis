import unittest
import pandas as pd
import numpy as np
from src.anomaly_detection.dimensionality_reduction import *
from src.anomaly_detection.isolation_forests import *
from src.anomaly_detection.oneclass_svm import *
from src.anomaly_detection.preprocessing_ohe import *

class AnomalyDetectionTestCase(unittest.TestCase):
    def test_preprocessing_review(self):
        df=pd.DataFrame({
            "Result by Reviewer A":[np.NaN,np.NaN,np.NaN],
            "Result by Reviewer B":[np.NaN,np.NaN,'reject'],
            "Result by Reviewer C":[np.NaN,np.NaN,np.NaN],
            "Result by Reviewer X":[np.NaN,np.NaN,np.NaN],
            "accepts":[np.NaN,np.NaN,np.NaN],
            "case:concept:name":[1,1,1],
            "case:description":['Simulated process instance','Simulated process instance','Simulated process instance'],
            "concept:name":["invite reviewers","invite reviewers", "get review 2"],
            "lifecycle:transition":["start","complete","complete"],
            "org:resource":["Mike","Mike","Carol"],
            "rejects":[np.NaN,np.NaN,np.NaN],
            "time:timestamp":['2006-01-01 00:00:00+01:00','2006-01-06 00:00:00+01:00','2006-01-09 00:00:00+01:00']
        })

        res=pd.DataFrame({
            "onehotencoder__Result by Reviewer A_nan":[1.0,1.0,1.0],
            "onehotencoder__Result by Reviewer B_reject":[0.0,0.0,1.0],
            "onehotencoder__Result by Reviewer B_nan":[1.0,1.0,0.0],
            "onehotencoder__Result by Reviewer C_nan":[1.0,1.0,1.0],
            "onehotencoder__Result by Reviewer X_nan":[1.0,1.0,1.0],
            "onehotencoder__concept:name_get review 2":[0.0,0.0,1.0],
            "onehotencoder__concept:name_invite reviewers":[1.0,1.0,0.0],
            "onehotencoder__lifecycle:transition_complete":[0.0,1.0,1.0],
            "onehotencoder__lifecycle:transition_start":[1.0,0.0,0.0],
            "onehotencoder__org:resource_Carol":[0.0,0.0,1.0],
            "onehotencoder__org:resource_Mike":[1.0,1.0,0.0],
            "onehotencoder__case:description_Simulated process instance":[1.0,1.0,1.0],
            "remainder__accepts":['0','0','0'],
            "remainder__case:concept:name":[1,1,1],
            "remainder__rejects":['0','0','0'],
            "remainder__time:timestamp":[1136070000.0,1136502000.0,1136761200.0]
        })

        self.assertListEqual(preprocessing_review(df).values.tolist(),res.values.tolist())


    def test_preprocessing_receipt(self):
        
        datas = [
        ['Internet', 'case-10011', 'General', 'Group 2', 'Resource21', 'task-42933', 'Confirmation of receipt', 'complete', 'Group 1', 'Resource21', '2011-10-11 13:45:40.276000+02:00'],
        ['Internet', 'case-10011', 'General', 'Group 2', 'Resource21', 'task-42935', 'T02 Check confirmation of receipt', 'complete', 'Group 4', 'Resource10', '2011-10-12 08:26:25.398000+02:00'],
        ['Internet', 'case-10011', 'General', 'Group 2', 'Resource21', 'task-42957', 'T03 Adjust confirmation of receipt', 'complete', 'Group 1', 'Resource21', '2011-11-24 15:36:51.302000+01:00']
        ]

        columnss = ['case:channel', 'case:concept:name', 'case:department', 'case:group', 'case:responsible', 'concept:instance', 'concept:name', 'lifecycle:transition', 'org:group', 'org:resource', 'time:timestamp']

        df=pd.DataFrame(datas,columns=columnss)

        data = [
            [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 10011, 1318333540.276],
            [1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 10011, 1318400785.398],
            [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 10011, 1322145411.302]
        ]

        columns = [
        'onehotencoder__case:channel_Internet',
        'onehotencoder__case:department_General',
        'onehotencoder__case:group_Group 2',
        'onehotencoder__case:responsible_Resource21',
        'onehotencoder__concept:instance_task-42933',
        'onehotencoder__concept:instance_task-42935',
        'onehotencoder__concept:instance_task-42957',
        'onehotencoder__concept:name_Confirmation of receipt',
        'onehotencoder__concept:name_T02 Check confirmation of receipt',
        'onehotencoder__concept:name_T03 Adjust confirmation of receipt',
        'onehotencoder__lifecycle:transition_complete',
        'onehotencoder__org:group_Group 1',
        'onehotencoder__org:group_Group 4',
        'onehotencoder__org:resource_Resource10',
        'onehotencoder__org:resource_Resource21',
        'remainder__case:concept:name',
        'remainder__time:timestamp'
        ]
        res=pd.DataFrame(data,columns=columns)
        self.assertListEqual(preprocessing_receipt(df).values.tolist(),res.values.tolist())
        
    def test_pca(self):
        df=pd.DataFrame({
            "onehotencoder__Result by Reviewer A_nan":[1.0,1.0,1.0],
            "onehotencoder__Result by Reviewer B_reject":[0.0,0.0,1.0],
            "onehotencoder__Result by Reviewer B_nan":[1.0,1.0,0.0],
            "onehotencoder__Result by Reviewer C_nan":[1.0,1.0,1.0],
            "onehotencoder__Result by Reviewer X_nan":[1.0,1.0,1.0],
            "onehotencoder__concept:name_get review 2":[0.0,0.0,1.0],
            "onehotencoder__concept:name_invite reviewers":[1.0,1.0,0.0],
            "onehotencoder__lifecycle:transition_complete":[0.0,1.0,1.0],
            "onehotencoder__lifecycle:transition_start":[1.0,0.0,0.0],
            "onehotencoder__org:resource_Carol":[0.0,0.0,1.0],
            "onehotencoder__org:resource_Mike":[1.0,1.0,0.0],
            "onehotencoder__case:description_Simulated process instance":[1.0,1.0,1.0],
            "remainder__accepts":['0','0','0'],
            "remainder__case:concept:name":[1,1,1],
            "remainder__rejects":['0','0','0'],
            "remainder__time:timestamp":[1.13607,1.136502,1.136761]
        })
        res=[[-1.09441231,-0.59817828],[-0.60037683,0.72693641],[ 1.69478914,-0.12875814]]

        x=pca(df)

        for i in range(0,2):
            for j in range(0,1):
                self.assertAlmostEqual(x[i][j],res[i][j],2)

if __name__ == '__main__':
    unittest.main()
