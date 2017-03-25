from v1 import app
from flask import jsonify, request, abort, make_response, url_for
import sqlite3

def get_connection():
    return sqlite3.connect("todos.db")

def insert_record(json):
    dict = {'detalle':json['detalle'], 'fecha': json['fecha']}
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO todo values (null, :detalle, :fecha)", dict)
    conn.commit()
    conn.close()
    return dict;

def get_record(id):
    conn = get_connection()
    cur = conn.cursor()
    res = cur.execute("SELECT fecha, detalle FROM todo WHERE id=?", (id, ))
    ret = res.fetchone()
    conn.close()
    return ret

def update_record(json):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE todo SET detalle = :detalle, fecha = :fecha WHERE id = :id", json)
    conn.commit()
    conn.close()

def delete_record(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM todo WHERE id = ?",(id,))
    conn.commit()
    conn.close()

def make_public_task(task):
    new_task={}
    new_task['uri'] = url_for('get_task', task_id=task[0], _external=True)
    new_task['detalle'] = task[1]
    new_task['fecha'] = task[2]

    return new_task

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route("/todo/api/v1.0/tasks/<int:task_id>", methods = ["DELETE"])
def delete_task(task_id):
    record = get_record(task_id)
    if record == None or len(record) == 0:
        abort(404)
    delete_record(task_id)
    return jsonify({'result': True})

@app.route("/todo/api/v1.0/tasks/<int:task_id>", methods = ["PUT"])
def update_task(task_id):
    record = get_record(task_id)
    dict = {"id": task_id}
    if record == None:
        abort(404)
    if 'detalle' in request.json:
        dict['detalle'] = request.json['detalle']
    else:
        dict['detalle'] = record['detalle']

    if 'fecha' in request.json:
        dict['fecha'] = request.json['fecha']
    else:
        dict['fecha'] = record['fecha']

    update_record(dict)
    #Buscar registro actualizado
    record = get_record(task_id)
    return jsonify({'task': record})

@app.route("/todo/api/v1.0/tasks", methods = ["POST"])
def create_task():
    if not request.json or not 'fecha' in request.json \
            or not 'detalle' in request.json:
        abort(400)
    res = insert_record(request.json)
    return jsonify({'task': res}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['GET'])
def get_task(task_id):
    record = get_record(task_id)
    if record == None or len(record) <=0:
        abort(404)
    return jsonify({"task":{"detalle":record[0], "fecha": record[1]}})

@app.route('/todo/api/v1.0/tasks', methods = ['GET'])
def get_tasks():
    conn = get_connection()
    cursor = conn.cursor().execute("SELECT id, detalle, fecha FROM todo")
    data = cursor.fetchall()
    conn.close()
    #tasks = {}
    if len(data) <= 0:
        return jsonify({"results": "no records in the table"})
    else:
        return jsonify({"todos" : [make_public_task(task) for task in data]})
