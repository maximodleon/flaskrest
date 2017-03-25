from flask import Flask
import sqlite3

"""
 Crear base de datos cuando empieza la aplicacion, crear tabla para almacenar los datos si no existe
 y borrar los datos en caso de que tenga algo.
 
"""
conn = sqlite3.connect("todos.db")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS todo (id integer primary key autoincrement, fecha text, detalle text)")

conn.commit()
conn.close()

app = Flask(__name__)
from v1 import api
