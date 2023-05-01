from flask import Flask, url_for, jsonify, abort, request, flash, session
from flask_session import Session
import pymysql
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

conn = pymysql.connect(
    host='44.202.86.217',
    user='user1',
    password='SO-SC51',
    database='RemindMeDB' 
)

cursor = conn.cursor()

@app.route('/login',  methods=['POST'])
def login():
    username = request.form.get("username")
    passw = request.form.get("password")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM User WHERE  username=%s', (username))
    result = cursor.fetchone()
    if check_password_hash(result[3],passw):
        session["id"] = result[0]
        session["username"] = username
        session["email"] = result[2]
        session["password"] = passw
        user = {
            "username": session["username"],
            "email" : session["email"],
            "password" : session["password"] 
        }
        return jsonify(user)
    else:
        abort(401)

@app.route('/logout')   
def logout():
    if 'id' not in session:
        abort(401)
    user = {
        "username": session["username"],
        "email" : session["email"],
        "password" : session["password"] 
    }
    session.pop("id")
    return jsonify(user)

@app.route('/tasks')
def tasks():
    if 'id' not in session:
        abort(401)
    cursor.execute('SELECT * FROM Task where idUser = %s', (session['id']))
    data = cursor.fetchall()
    tasks = []
    for row in data:
        task = {
            "id": row[0],
            "name": row[1],
            "status": row[2],
            "date": row[3],
        }
        tasks.append(task)

    return jsonify(tasks)

@app.route('/addtask', methods=['POST'])
def addtask():
    task = request.form.get('task')
    status = request.form.get('status')
    tag_name = request.form.get('tag')
    date = request.form.get('deadline')

    cursor = conn.cursor()
    cursor.execute('SELECT idTag FROM Tag WHERE name=%s AND idUser=%s;', (tag_name,session["id"]))
    result = cursor.fetchone()
    tag_id = result[0] if result else None

    cursor.execute('SELECT MAX(idTask) FROM Task;')
    result = cursor.fetchone()
    idTask = result[0]+1 if result[0] != None else 0
    if tag_id is not None:
        cursor.execute('INSERT INTO Task (idTask, name, status, date, idUser, idTag) VALUES (%s, %s, %s, %s, %s, %s)',
                    (idTask, task, status, date, session["id"], tag_id))
    else:
        cursor.execute('INSERT INTO Task (idTask, name, status, date, idUser, idTag) VALUES (%s, %s, %s, %s, %s, NULL)',
                (   idTask, task, status, date,session["id"]))
    conn.commit()
    task = {
        "id": idTask,
        "name": task,
        "status": status,
        "date": date
    }
    return jsonify(task)

@app.route('/editTask',methods=['POST'])
def editTask():
    idTask = request.form.get('idTask')
    task = request.form.get('task')
    status = request.form.get('status')
    tag_name = request.form.get('tag')
    date = request.form.get('deadline')

    cursor = conn.cursor()
    cursor.execute('SELECT idTag FROM Tag WHERE name=%s AND idUser=%s;', (tag_name,session["id"]))
    result = cursor.fetchone()
    tag_id = result[0] if result else None
    
    if tag_id is not None:
        cursor.execute('UPDATE Task SET name = %s, status = %s, date = %s, idTag = %s WHERE idTask = %s',
                    (task, status, date, tag_id, idTask))
    else:
        cursor.execute('UPDATE Task SET name = %s, status = %s, date = %s WHERE idTask = %s',
                    (task, status, date, idTask))
    conn.commit()
    task = {
        "id": idTask,
        "name": task,
        "status": status,
        "date": date
    }
    return jsonify(task)

@app.route('/deleteTask',methods=['POST'])
def deleteTask():
    idTask = request.form.get('idTask')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Task where idTask=%s;',(idTask))
    result = cursor.fetchone()
    task = {
            "idTask": result[0],
            "name": result[1],
            "status": result[2],
            "date": result[3],
    }

    cursor.execute('DELETE FROM Subtask WHERE idTask = %s', (idTask))
    cursor.execute('DELETE FROM Task WHERE idTask = %s', (idTask))
    conn.commit()
    return jsonify(task)
    
@app.route('/tags')
def tags():
    if 'id' not in session:
        abort(401)
    cursor.execute('SELECT * FROM Tag where idUser = %s', (session['id']))
    data = cursor.fetchall()
    tags = []
    for row in data:
        tag = {
            "nombre de la etiqueta": row[1],
            "color": row[3]
        }
        tags.append(tag)

    return jsonify(tags)
@app.route('/addTag', methods=['POST'])
def addTag():
    tag = request.form.get('tag')
    color = request.form.get('color')
    
    cursor=conn.cursor()
    cursor.execute('SELECT MAX(idTag) FROM Tag')
    result=cursor.fetchone()
    idTag=result[0]+1 if result else 0
    cursor.execute('INSERT INTO Tag (idTag, name, idUser, color) VALUES (%s,%s,%s,%s)', (idTag, tag, session["id"], color))
    conn.commit()
    tag={
        "name": tag,
        "color": color
    }
    return jsonify(tag)

@app.route('/editTag', methods=['POST'])
def  editTag():
    idTag=request.form.get('idTag')
    tag=request.form.get('tag')
    color=request.form.get('color')

    cursor=conn.cursor()
    cursor.execute('UPDATE Tag SET name=%s, color=%s WHERE idTag=%s', (tag, color, idTag))
    conn.commit()
    tag={
        "Nuevo nombre": tag,
        "Color": color, 
        "status": "OK"
    }
    return jsonify(tag)

@app.route('/deleteTag', methods=['POST'])
def  deleteTag():
    idTag=request.form.get('idTag')
    cursor=conn.cursor()
    cursor.execute('DELETE FROM Task WHERE idTag=%s', (idTag))
    cursor.execute('DELETE FROM Tag WHERE idTag=%s', (idTag))
    conn.commit()
    tag={
        "status": "Se borro la etiqueta correctamente"
    }
    return jsonify(tag)

@app.route('/subtaskss')
def subtasks():
    if 'id' not in session:
        abort(401)
    idTask = request.form.get("idTask")
    cursor.execute('SELECT * FROM Subtask where idTask = %s', (idTask))
    data = cursor.fetchall()
    subs = []
    for row in data:
        sub = {
            "Nombre de la sub tarea": row[1],
            "description": row[2],
        }
        subs.append(sub)

    return jsonify(subs)

@app.route('/subtasks')
def subtasks():
    if 'id' not in session:
        abort(401)
    cursor.execute('SELECT idTask FROM Task')
    data = cursor.fetchall()
    subs = []
    for idtks in data:
        cursor.execute('SELECT name FROM Task where idTask=%s', (idtks[0]))
        nm=cursor.fetchall()
        cursor.execute('SELECT * FROM Subtask where idTask=%s', (idtks[0]) )
        newdata=cursor.fetchall()
        for row in newdata:
            sub={
                "Tarea": nm[0],
                "Sub Tarea": row[1],
                "Descripcion": row[2]
            }
            subs.append(sub)
    return jsonify(subs)
            
@app.route('/addSubtask', methods=['POST'])
def addSubtask():
    idTask = request.form.get('idTask')
    subTask = request.form.get('subTask')
    description = request.form.get('description')
    
    cursor=conn.cursor()
    cursor.execute('SELECT MAX(idSubtask) FROM Subtask')
    result=cursor.fetchone()
    idSubtask=result[0]+1 if result else 0
    cursor.execute('INSERT INTO Subtask (idSubtask, name, description, idTask) VALUES (%s,%s,%s,%s)', (idSubtask, subTask, description, idTask))
    conn.commit()

    cursor=conn.cursor()
    cursor.execute('SELECT name from Task where idTask=%s', (idTask))
    result=cursor.fetchone()
    task=result[0]
    subTask={
        "Tarea": task,
        "Subtarea": subTask,
        "Descripcion": description,
        "status": "OK"
    }
    return jsonify(subTask)

@app.route('/editSubtask', methods=['POST'])
def editSubtask():
    idSubtask = request.form.get('idSubtask')
    subTask = request.form.get('subTask')
    description = request.form.get('description')
    
    cursor=conn.cursor()
    cursor.execute('UPDATE Subtask SET name=%s, description=%s WHERE idSubtask=%s', (subTask, description, idSubtask))
    conn.commit()

    subTask={
        "Subtarea renombrada": subTask,
        "Nueva descripcion": description,
        "status": "OK"
    }
    return jsonify(subTask)

@app.route('/deleteSubtask', methods=['POST'])
def deleteSubtask():
    idSubtask = request.form.get('idSubtask')  
    cursor=conn.cursor()
    cursor.execute('delete from Subtask where idSubtask=%s', (idSubtask))
    conn.commit()
    subTask={
        "status": "OK"
    }
    return jsonify(subTask)