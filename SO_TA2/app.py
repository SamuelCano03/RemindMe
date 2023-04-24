from flask import Flask, url_for, render_template, request, redirect, flash,session
from flask_session import Session
from markupsafe import escape
import mysql.connector
import pymysql
from datetime import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

conn = pymysql.connect(
    host='3.82.153.28',
    user='user1',
    password='SO-SC51',
    database='RemindMeDB'
)

cursor = conn.cursor()


@app.route('/')
def basic():
    return redirect('/index')

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/login',  methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        passw = request.form.get("password")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE  username=%s AND password=%s', (username, passw))
        result = cursor.fetchone()
        if result:
            session["id"] = result[0]
            session["username"] = username
            session["email"] = result[2]
            session["password"] = passw
            return redirect('home')
        else:
            flash("Usuario o contraseña incorrecta")
            return render_template("login.html")
    else:
        return render_template("login.html")
    
@app.route('/signup',  methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        passw = request.form.get('password')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE username=%s OR email=%s ', (username,email))
        result = cursor.fetchone()
        if result:
            flash("El nombre de usuario o correo ya esta registrado")
            return render_template('signup.html')
        else:
            cursor.execute('SELECT MAX(idUser) FROM User;')
            result = cursor.fetchone()
            userId = result[0] + 1 if result else 0
            cursor.execute('INSERT INTO User (idUser, username, email, password) VALUES (%s,%s, %s, %s)',
                       (userId, username,email, passw))
            conn.commit()
            return redirect('login')
    else:
        return render_template('signup.html')
    
@app.route('/logout')   
def logout():
    session.pop("id")
    return redirect("index")

@app.route('/home')
def home():
    if 'id' not in session:
        return redirect('/login')
    cursor.execute('SELECT * FROM Task where idUser = %s', (session['id']))
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM Tag where idUser = %s', (session['id']))
    tags = cursor.fetchall()
    cursor.execute('SELECT Subtask.idTask, Subtask.name, Subtask.description, Subtask.idSubtask FROM Task JOIN Subtask on Task.idTask = Subtask.idTask where Task.idUser = %s', (session['id']))
    sub = cursor.fetchall()
    return render_template("home.html",data=data, tags=tags, sub=sub)

@app.route('/config', methods=['POST', 'GET'] )
def config():
    return render_template("config.html")

@app.route('/configEdit', methods=['POST', 'GET'] )
def configEdit():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE username=%s OR email=%s ', (username,email))
        result = cursor.fetchone()
        if result and (username != session["username"] and email != session["email"]):
            return redirect('/config')
        else:
            cursor.execute('UPDATE User SET username = %s, email = %s, password = %s  WHERE idUser = %s', (username, email, password, session['id']))
            session["username"] = username
            session["email"] = email
            session["password"] = password
            conn.commit()
        return redirect('/config')
    return redirect('/config')

@app.route('/configDelete', methods=['POST', 'GET'] )
def configDelete():
    if request.method == 'POST':
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Task WHERE idUser = %s', (session['id']))
        cursor.execute('DELETE FROM Tag WHERE idUser = %s', (session['id']))
        cursor.execute('DELETE FROM User WHERE idUser = %s', (session['id']))
        conn.commit()
        return redirect('/index')
    else:
        return redirect('/config')

@app.route('/addtask', methods=['POST', 'GET'])
def addtask():
    if request.method == 'POST':
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
        idTask = result[0]+1 if result else 0
        if tag_id is not None:
            cursor.execute('INSERT INTO Task (idTask, name, status, date, idUser, idTag) VALUES (%s, %s, %s, %s, %s, %s)',
                        (idTask, task, status, date, session["id"], tag_id))
        else:
            cursor.execute('INSERT INTO Task (idTask, name, status, date, idUser, idTag) VALUES (%s, %s, %s, %s, %s, NULL)',
                    (   idTask, task, status, date,session["id"]))
        conn.commit()
        return redirect('home')
    return redirect('home')

@app.route('/addtag', methods=['POST', 'GET'])
def addtag():
    if request.method == 'POST':
        tagname = request.form.get('tagname')
        color = request.form.get('color')

        cursor = conn.cursor()
        cursor.execute('SELECT MAX(idTag) FROM Tag;')
        result = cursor.fetchone()
        tag_id = result[0]+1 if result[0] != None else 0
        cursor.execute('INSERT INTO Tag (idTag, name, idUser) VALUES (%s,%s,%s)', (tag_id, tagname, session["id"]))
        conn.commit()
        return redirect('home')
    else:
        return redirect('home')
    
@app.route('/addsubtask/<int:idTask>', methods=['POST', 'GET'])
def addsubtask(idTask):
    if request.method == 'POST':
        subtask = request.form.get('subtask')
        description = request.form.get('description')

        cursor = conn.cursor()
        cursor.execute('SELECT MAX(idSubtask) FROM Subtask;')
        result = cursor.fetchone()
        sub_id = result[0]+1 if result[0] != None else 0
        cursor.execute('INSERT INTO Subtask (idSubtask, name, description, idTask) VALUES (%s,%s,%s,%s)', (sub_id, subtask,description, idTask))
        conn.commit()
        return redirect('/home')
    else:
        return redirect('/home')

@app.route('/editTask/<int:idTask>',methods=['POST', 'GET'])
def editTask(idTask):
    if request.method == 'POST':
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
        return redirect('/home')
    else:
        return redirect('/home')

@app.route('/deleteTask/<int:idTask>',methods=['POST', 'GET'])
def deleteTask(idTask):
    if request.method == 'POST':
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Subtask WHERE idTask = %s', (idTask))
        cursor.execute('DELETE FROM Task WHERE idTask = %s', (idTask))
        conn.commit()
        return redirect('/home')
    else:
        return redirect('/home')

@app.route('/deleteSubtask/<int:idSubtask>',methods=['POST', 'GET'])
def deleteSubtask(idSubtask):
    if request.method == 'POST':
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Subtask WHERE idSubtask = %s', (idSubtask))
        conn.commit()
        return redirect('/home')
    else:
        return redirect('/home')