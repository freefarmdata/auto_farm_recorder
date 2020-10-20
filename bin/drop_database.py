import psycopg2 as postgres

con = postgres.connect(
  database="farmdata",
  user="admin",
  password="admin",
  host="0.0.0.0",
  port="5432"
)

cur = con.cursor()

cur.execute('DROP TABLE soil')
cur.execute('DROP TABLE ds18b20')
cur.execute('DROP TABLE dht11')

con.commit()