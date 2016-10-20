"""write tasks to a json file with remaining numbers
The flask server will maintain the right number of tasks.
number - =1 when a task is assigned
number += 1 when a user quit early

Three parameters: targetR , starting distance and mode(Above or Below)"""


import json
mode_list= ["Above","Below"]
targetR_list = [0.4,0.5,0.6,0.7,0.8]
distance_dic = {0.4:0.2,0.5:0.2,0.6:0.1,0.7:0.1,0.8:0.1}
trial_num =1

data = {}

for m in mode_list:
    for t in targetR_list:
        task = m +":"+ str(t)+":" + str(distance_dic[t])
        print task
        data[task] = trial_num
print data

with open('task.json', 'w') as outfile:
    json.dump(data, outfile)

with open('task.json', 'r') as outfile:
    data2 = json.load(outfile)
print data2
total_number = len(data)*trial_num
print total_number