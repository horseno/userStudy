from sqlalchemy import create_engine, MetaData, Table
import json
import pandas as pd
import os

#DB settings
db_url = "sqlite:///../participants-04.db"
table_name = 'turkdemo'
data_column_name = 'datastring'
#Reject rule settings
obvious_range={0.2:(0,0.8),0.3:(0,0.8),0.4:(0,0.8),0.5:(0.2,0.8),0.6:(0.3,0.9),0.7:(0.4,0.9)}
#Any value out of the range should be obviously distinguishable by a user with understanding of correlation.


def load_from_db(data_path):
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.bind = engine
    table = Table(table_name, metadata, autoload=True)
    # make a query and loop through
    s = table.select()
    rows = s.execute()  

    data = []
    question_data =[] # a stand alone file with feed backs 
    #status codes of subjects who completed experiment
    statuses = [3,4,5,7]
    # if you have workers you wish to exclude, add them here
    exclude = []
    for row in rows:
        # only use subjects who completed experiment and aren't excluded
        if row['status'] in statuses and row['uniqueid'] not in exclude:
            #data.append(row[data_column_name]) 

            data = json.loads(row[data_column_name])['data']
            question = json.loads(row[data_column_name])['questiondata']

            for record in data:
                record['trialdata']['uniqueid'] = record['uniqueid']
                uniqueid = record['uniqueid'].split(":")[1] 

            question['uniqueid']= data[0]['uniqueid']
            question_data.append(question)
            
            data = [record['trialdata'] for record in data]
            data.append(question)
            data_frame = pd.DataFrame(data)
            data_frame.to_csv(data_path+str(uniqueid)+".csv")

    pd.DataFrame(question_data).to_csv("feedback.csv")

def if_reject(fileName,data_path):
    """detemines if to reject an assignment by a set of rules"""
    dataFrame = pd.read_csv(data_path+fileName)
    df = dataFrame.loc[dataFrame['phase'] == "TEST"]

    targetR = df.iloc[0]['targetR']
    response_l = len(df.loc[df['response']=='Left'])
    if ((response_l == 0 ) or (response_l == len(df))): 
        return True

    short_response = df.loc[df['rt']<500]
    if (len(short_response)>3):
        return True

    lb,up = obvious_range[targetR]
    obvious_repsonses = df.loc[ ((df['variableR']> up) | (df['variableR']< lb) & (df['hit']==False) ) ]
    if (len(obvious_repsonses)>5):
        return True

    hit_rate = float(len(df.loc[df['hit']==True]))/len(df)
    if (hit_rate<=0.5):
        return True

    return False

def pre_process(data_path,approve_list,reject_list):
    """read data from database and produce the reject/approve list"""

    load_from_db(data_path)

    approve_f = open(approve_list, 'a')
    reject_f = open(reject_list, 'a')   

    for fileName in os.listdir(data_path):
        assignmentID = fileName.split(".")[0]   

        if if_reject(fileName,data_path):
            reject_f.write(assignmentID)
            reject_f.write(" ")
        else:
            approve_f.write(assignmentID)
            approve_f.write(" ")