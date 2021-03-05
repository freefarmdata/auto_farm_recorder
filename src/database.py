#import psycopg2 as postgres
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
      CREATE TABLE IF NOT EXISTS water (
        id SERIAL PRIMARY KEY,
        start TIMESTAMP NOT NULL,
        end TIMESTAMP NOT NULL
      );
      '''
    )
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


def insert_watertime(start, end):
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      "INSERT INTO water (start, end) VALUES (%s, %s)",
      (start, end)
    )
    connection.commit()


def insert_timeseries(table, readings):
  with get_connection() as connection:
    cursor = connection.cursor()
    now = datetime.datetime.utcnow()
    for reading in readings:
      cursor.execute(
        f"INSERT INTO {table} (board_id, sensor, value, timestamp) VALUES (%s, %s, %s, %s)",
        (reading['board_id'], reading['sensor'], reading['value'], now)
      )
    connection.commit()


def series_dict(tupl):
  if tupl:
    id, board_id, sensor, value, timestamp = tupl
    return {
      'id': id,
      'board_id': board_id,
      'sensor': sensor,
      'value': value,
      'timestamp': timestamp,
    }


def water_dict(tupl):
  if tupl:
    id, start, end = tupl
    return {
      'id': id,
      'start': start,
      'end': end,
    }


def query_latest_watering(amount=1):
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      f"SELECT * FROM watering ORDER BY end LIMIT %s",
      (amount)
    )
    records = cursor.fetchall()
    records = [water_dict(r) for r in records]
  return records


def query_for_first_soil():
  record = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      f"SELECT * FROM soil ORDER BY timestamp LIMIT 1"
    )
    record = series_dict(cursor.fetchone())
  return record


def query_for_latest_soil(amount=1):
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      f"SELECT * FROM soil ORDER BY timestamp LIMIT %s",
      (amount)
    )
    records = cursor.fetchall()
    records = [series_dict(r) for r in records]
  return records


def query_for_soil(start_time, end_time):
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      f"SELECT * FROM soil WHERE timestamp BETWEEN %s AND %s",
      (start_time, end_time)
    )
    records = cursor.fetchall()
    records = [series_dict(r) for r in records]
  return records