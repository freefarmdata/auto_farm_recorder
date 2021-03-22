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


def reset_all():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS models;')
    cursor.execute('DROP TABLE IF EXISTS water;')
    cursor.execute('DROP TABLE IF EXISTS soil;')
    cursor.execute('DROP TABLE IF EXISTS temp;')
    cursor.execute('DROP TABLE IF EXISTS light;')
    cursor.execute('DROP TABLE IF EXISTS pressure;')
    connection.commit()

def reset_data():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS soil;')
    cursor.execute('DROP TABLE IF EXISTS temp;')
    cursor.execute('DROP TABLE IF EXISTS light;')
    cursor.execute('DROP TABLE IF EXISTS pressure;')
    connection.commit()


def initialize():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS models (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        active BOOLEAN NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        error NUMERIC NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS water (
        id SERIAL PRIMARY KEY,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL
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
        value NUMERIC NOT NULL,
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
        value NUMERIC NOT NULL,
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
        value NUMERIC NOT NULL,
        timestamp TIMESTAMP NOT NULL
      );
      '''
    )
    connection.commit()


def insert_watertime(start, end):
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      "INSERT INTO water (start_time, end_time) VALUES (%s, %s)",
      (start, end)
    )
    connection.commit()


def insert_timeseries(table, readings):
  with get_connection() as connection:
    cursor = connection.cursor()
    now = datetime.datetime.now()
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
      'timestamp': float(timestamp.timestamp()),
    }


def water_dict(tupl):
  if tupl:
    id, start, end = tupl
    return {
      'id': id,
      'start_time': float(start.timestamp()),
      'end_time': float(end.timestamp()),
    }


def model_dict(tupl):
  if tupl:
    id, name, active, start, end, error = tupl
    return {
      'id': id,
      'name': name,
      'active': active,
      'start_time': float(start.timestamp()),
      'end_time': float(end.timestamp()),
      'error': float(error),
    }


def query_for_watering():
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM water ORDER BY end_time")
    records = cursor.fetchall()
    records = [water_dict(r) for r in records]
  return records


def query_latest_watering(amount=1):
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      f"SELECT * FROM water ORDER BY end_time LIMIT %s",
      (str(amount))
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
      (str(amount))
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


def query_for_models():
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM models ORDER BY end_time")
    records = cursor.fetchall()
    records = [model_dict(r) for r in records]
  return records


def delete_model(name):
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      "DELETE FROM models WHERE name = %s",
      (name,)
    )
    connection.commit()


def insert_model(name, start, end, error):
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      "INSERT INTO models (name, active, start_time, end_time, error) VALUES (%s, %s, %s, %s, %s)",
      (name, False, start, end, error)
    )
    connection.commit()


def get_active_model():
  records = None
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM models WHERE active IS TRUE")
    records = cursor.fetchall()
    records = [model_dict(r) for r in records]
  return records


def set_model_active(name):
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute("UPDATE models SET active = FALSE WHERE active IS TRUE")
    cursor.execute(
      f"UPDATE models SET active = TRUE WHERE name = '{name}'"
    )
    connection.commit()