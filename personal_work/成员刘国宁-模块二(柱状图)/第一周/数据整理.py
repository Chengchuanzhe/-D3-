import json
import numpy as np

with open('coupled_data.json', 'r') as f:
    data = json.load(f)
# 处理数据
Day = [d['date'] for d in data]
pressure = [d['pressure'] for d in data]
pre = []
pre.append(pressure[0])
day = []
day.append(Day[0])
m = 0
while(m<len(pressure)-1):
    pre.append(np.round(np.mean(pressure[m+1:m+25]),1))
    day.append(Day[m+1])
    m=m+24 

output = {
    "day":day,
    "pressure":pre
}

with open("pressure-day.json","w") as f:
    json.dump(output, f, allow_nan=False)