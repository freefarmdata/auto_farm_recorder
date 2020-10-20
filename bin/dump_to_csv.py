import csv
import os
import time
import psycopg2 as postgres

def get_connection():
    return postgres.connect(
        database="farmdata",
        user="admin",
        password="admin",
        host="0.0.0.0",
        port="5432"
    )

connection = get_connection()
cursor = connection.cursor()

tables = {
    'soil': 'SELECT id, sensor, value, timestamp FROM soil',
    'ds18b20': 'SELECT id, sensor, value, timestamp FROM ds18b20',
    'dht11': 'SELECT id, sensor, temp, humid, timestamp from dht11'
}

for table in tables:
    select = tables[table]
    cursor.execute(select)
    headers = [i[0] for i in cursor.description]

    now_ms = int(time.time()*1000)
    file_path = f'{table}_{now_ms}.csv'
    print(f'Writing {table} to {file_path}')

    csv_file = csv.writer(
        open(file_path, 'w', newline=''),
        delimiter=',',
        lineterminator='\n',
        quoting=csv.QUOTE_ALL,
        escapechar='\\'
    )

    csv_file.writerow(headers)

    n = 100
    while True:
        results = cursor.fetchmany(n)
        if len(results) <= 0:
            break
        csv_file.writerows(results)

connection.close()
