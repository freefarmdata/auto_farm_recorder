import psycopg2 as postgres
import datetime

def get_connection():
  return postgres.connect(
    database="farmdata",
    user="admin",
    password="admin",
    host="0.0.0.0",
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
        timestamp TIMESTAMP NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS temp (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        value REAL NOT NULL,
        timestamp TIMESTAMP NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS light (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        value REAL NOT NULL,
        timestamp TIMESTAMP NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS pressure (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        value REAL NOT NULL,
        timestamp TIMESTAMP NOT NULL
      );
      '''
    )
    connection.commit()

def insert_timeseries(table, readings):
  with get_connection() as connection:
    cursor = connection.cursor()
    for reading in readings:
      cursor.execute(
        "INSERT INTO %s (sensor, value, timestamp) VALUES (%s, %s, %s)",
        (table, reading.get('pin'), reading.get('value'), datetime.datetime.utcnow())
      )
    connection.commit()