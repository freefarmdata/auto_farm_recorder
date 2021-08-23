import psycopg2 as postgres
import datetime

from fservice import state

def get_connection():
  host = state.get_global_setting('database_host')
  return postgres.connect(
    database="farmdata",
    user="admin",
    password="admin",
    host=host,
    port=5432
  )


def reset_all():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS watering;')
    cursor.execute('DROP TABLE IF EXISTS readings;')
    connection.commit()


def initialize():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS watering (
        id SERIAL PRIMARY KEY,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS readings (
        id SERIAL PRIMARY KEY,
        board TEXT NOT NULL,
        metric TEXT NOT NULL,
        sensor INT NOT NULL,
        value INT NOT NULL,
        timestamp TIMESTAMP NOT NULL
      );
      '''
    )
    connection.commit()


def insert_watertime(start, end):
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      "INSERT INTO watering (start_time, end_time) VALUES (%s, %s)",
      (start, end)
    )
    connection.commit()


def insert_readings(readings):
  """
  columns:
    id - primary key
    board - the name of the board
    metric - the sensor metric value
    sensor - the sensor number
    value - the value
    timestamp - the timestamp
  """
  with get_connection() as connection:
    cursor = connection.cursor()
    for reading in readings:
      cursor.execute(
        f"INSERT INTO readings (board, metric, sensor, value, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (reading['board'], reading['metric'], reading['sensor'], reading['value'], reading['timestamp'])
      )
    connection.commit()


def reading_dict(tupl):
  if tupl:
    id, board, metric, sensor, value, timestamp = tupl
    return {
      'id': id,
      'board': board,
      'metric': metric,
      'sensor': sensor,
      'value': value,
      'timestamp': float(timestamp.timestamp()),
    }


def watering_dict(tupl):
  if tupl:
    id, start, end = tupl
    return {
      'id': id,
      'start_time': float(start.timestamp()),
      'end_time': float(end.timestamp()),
    }


def query_for_watering():
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM watering ORDER BY end_time")
    records = cursor.fetchall()
    records = [watering_dict(r) for r in records]
  return records


def query_latest_watering(amount=1):
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      f"SELECT * FROM watering ORDER BY end_time LIMIT %s",
      (str(amount))
    )
    records = cursor.fetchall()
    records = [watering_dict(r) for r in records]
  return records


def query_latest_soil(board='', sensor=0):
  record = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      """
      SELECT * FROM readings
      WHERE metric = 'soil' AND board = %s AND sensor = %s
      ORDER BY timestamp LIMIT 1
      """,
      (board, sensor)
    )
    record = reading_dict(cursor.fetchone())
  return record


def query_for_soil(board='', sensor=0, start_time='', end_time=''):
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      """
      SELECT * FROM soil
      WHERE metric = 'soil' AND board = %s AND sensor = %s AND timestamp BETWEEN %s AND %s 
      ORDER BY timestamp
      """,
      (board, sensor, start_time, end_time)
    )
    records = cursor.fetchall()
    records = [reading_dict(r) for r in records]
  return records