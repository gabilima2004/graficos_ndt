import json

with open('ndt_dashboard_parte3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed = 0
for panel in data['panels']:
    for target in panel.get('targets', []):
        sql = target.get('rawSql', '')
        
        # Pattern 1: Tables with UNION ALL - add server filter before GROUP BY "Provedor"
        if 'UNION ALL' in sql:
            if 'IN ($isp)\n    GROUP BY "Provedor"' in sql:
                sql = sql.replace(
                    'IN ($isp)\n    GROUP BY "Provedor"',
                    'IN ($isp)\n        AND d.server_site IN ($server)\n    GROUP BY "Provedor"'
                )
                fixed += 1
        
        # Pattern 2: Bar charts - add server filter before GROUP BY provedor
        elif 'IN ($isp)\nGROUP BY provedor' in sql:
            sql = sql.replace(
                'IN ($isp)\nGROUP BY provedor',
                'IN ($isp)\n    AND d.server_site IN ($server)\nGROUP BY provedor'
            )
            fixed += 1
        
        target['rawSql'] = sql

print(f"Queries fixed: {fixed}")

with open('ndt_dashboard_parte3.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("File saved")