import json

with open('ndt_dashboard_parte3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, panel in enumerate(data['panels']):
    for target in panel.get('targets', []):
        sql = target.get('rawSql', '')
        if 'IN ($isp)' in sql:
            idx = sql.find('IN ($isp)')
            snippet = sql[idx:idx+80]
            print(f"Panel {i} ({panel.get('title', 'no title')}): {repr(snippet)}")