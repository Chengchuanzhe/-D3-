import json
import numpy as np

with open('personal_work/成员刘国宁-模块二(柱状图)/第一周/Data.json', 'r',encoding='utf-8') as f:
    data = json.load(f)
# 处理数据
Day = [d['date'] for d in data if d["region_name"] == "台湾海峡"]
pressure = [d['pressure'] for d in data if d["region_name"] == "台湾海峡"]

output = {
    "day":Day,
    "pressure":pressure
}

with open('personal_work/成员刘国宁-模块二(柱状图)/第一周/pressure-day.json', 'w',encoding='utf-8') as f:
    json.dump(output, f, allow_nan=False)