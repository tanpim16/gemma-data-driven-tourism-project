import mysql.connector, sys

conn = mysql.connector.connect(
    host='viaduct.proxy.rlwy.net', port=56632,
    user='root', password='AKlHBzJLVWUESiEChqnbFvZHTxpYPhPw',
    database='railway', charset='utf8mb4', connection_timeout=15
)
cur = conn.cursor()
cur.execute('DESCRIBE saved_trips')
existing = {r[0] for r in cur.fetchall()}
print('existing:', existing)
for col, typ in [('loop_route','VARCHAR(500)'),('loop_highlights','LONGTEXT'),('estimated_budget_thb','INT')]:
    if col not in existing:
        cur.execute(f'ALTER TABLE saved_trips ADD COLUMN {col} {typ}')
        print('added:', col)
    else:
        print('skip:', col)
conn.commit()
conn.close()
print('done')
