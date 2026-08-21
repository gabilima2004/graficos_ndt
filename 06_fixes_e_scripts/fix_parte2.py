import re

with open('ndt_dashboard_parte2.json','r',encoding='utf-8') as f:
    txt=f.read()

old = 'GROUP BY 1, 3\nORDER BY 1 ASC",\n          "refId": "A",\n          "selectedFormat": 0'
new = 'GROUP BY "time", provedor\nORDER BY "time" ASC",\n          "refId": "A",\n          "selectedFormat": 0'

count = txt.count(old)
print('matches', count)
txt = txt.replace(old, new)

with open('ndt_dashboard_parte2.json','w',encoding='utf-8') as f:
    f.write(txt)
print('done')
