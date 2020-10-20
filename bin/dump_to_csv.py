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

tables = ['soil', 'ds18b20', 'dht11']

for table in tables:
    select = f'SELECT id, sensor, value, timestamp FROM {table}'
    cursor.execute(select)
    results = cursor.fetchall()
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
    csv_file.writerows(results)

connection.close()
