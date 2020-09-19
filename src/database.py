import sqlite3

DB_PATH = './database.db'

def get_connection():
  return sqlite3.connect(DB_PATH, check_same_thread=False)

def initialize():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS soil (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        value INT NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS ds18b20 (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        value REAL NOT NULL
      );
      '''
    )
    cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS dht11 (
        id SERIAL PRIMARY KEY,
        sensor INT NOT NULL,
        temp REAL NOT NULL,
        humid REAL NOT NULL
      );
      '''
    )
    connection.commit()

def insert_soil(readings):
  with get_connection() as connection:
    cursor = connection.cursor()
    for reading in readings:
      cursor.execute('INSERT INTO soil (sensor, value) VALUES (?, ?)', (reading.get("pin"), reading.get("value")))
    connection.commit()
    

