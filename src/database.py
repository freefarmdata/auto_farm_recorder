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


def reset():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute('DROP TABLE soil;')
    cursor.execute('DROP TABLE temp;')
    cursor.execute('DROP TABLE light;')
    cursor.execute('DROP TABLE pressure;')
    connection.commit()


def initialize():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS soil (
        id SERIAL PRIMARY KEY,
        board_id INT NOT NULL,
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
        board_id INT NOT NULL,
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
        board_id INT NOT NULL,
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
        board_id INT NOT NULL,
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
        "INSERT INTO %s (board_id, sensor, value, timestamp) VALUES (%s, %s, %s)",
        (table, reading['board_id'], reading['sensor'], reading['value'], datetime.datetime.utcnow())
      )
    connection.commit()