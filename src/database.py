import psycopg2 as postgres
import datetime

def iso_now():
  return datetime.datetime.now().isoformat()

def get_connection():
  return postgres.connect(
    database="farmdata",
    user="admin",
    password="admin",
    host="postgres",
    port="5432"
  )

def initialize():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS soil (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        value INT NOT NULL,
        timestamp TEXT NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS ds18b20 (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        value REAL NOT NULL,
        timestamp TEXT NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS dht11 (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        temp REAL NOT NULL,
        humid REAL NOT NULL,
        timestamp TEXT NOT NULL
      );
      '''
    )
    connection.commit()

def insert_soil(readings):
  with get_connection() as connection:
    cursor = connection.cursor()
    for reading in readings:
      cursor.execute(
        '''
        INSERT INTO soil (sensor, value, timestamp) 
        VALUES (?, ?, ?)
        ''',
        (reading.get("pin"), reading.get("value"), iso_now())
      )
    connection.commit()
    

