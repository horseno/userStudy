import os
import pandas as pd
import pre_process
import numpy as np

'''Retrieve data from DB and parse result to determine rejections.
   Rules: 
   - If all the responses are the same.
   - If there are more than 3 occurrences with rt<=500ms => reject 
   - If there are more than 5 occurrences with obvious wrong answers. 
   - If the error rate is higher than 50% (worse than random guesses)
'''


data_path = "./out/"
approve_list= "approve_list"
reject_list= "reject_list"

def get_seq(df):
    df = df.loc[df.loc[:,'phase'] == "TEST"]
    df.loc[:,"distance"] = abs(df.loc[:,'targetR'] -df.loc[:,'variableR'])
    return df.loc[:,'distance'].tolist()

pre_process.pre_process(data_path,approve_list,reject_list)

reject_f = open(reject_list, 'r') 
rejected = reject_f.readline().split(" ")


JND_dic = {0.2:[],0.3:[],0.4:[],0.5:[],0.6:[],0.7:[]}

for fileName in os.listdir(data_path):
        assignmentID = fileName.split(".")[0] 
        if not assignmentID in rejected:
            dataframe = pd.read_csv(data_path+fileName)
            dataframe = dataframe.loc[dataframe['phase'] == "TEST"]
            targetR = round(dataframe.iloc[0]['targetR'],2)
            distance = np.array(get_seq(dataframe))
            #print "targetR " + str(targetR)
            JND_dic[targetR].append(distance[-24:].mean())
            

for i in JND_dic:
    print i 
    print JND_dic[i]
    if len(JND_dic[i]):
        print sum(JND_dic[i])/float(len(JND_dic[i]))
#print JND_dic 

if __name__=="__main__":
    pass

    
