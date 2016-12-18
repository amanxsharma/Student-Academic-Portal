from flask import Flask,render_template,request,redirect,url_for
import sqlite3
sqlite_file='DATABASE.sqlite'
soft = Flask(__name__)
soft.secret_key = 'thisisdatabase'


@soft.route('/')
@soft.route('/<name>')
def index(name=None):
    return render_template('adminhomepage.html',text=name)


@soft.route('/validadmin',methods = ['POST', 'GET'])
def validadmin():
    user = request.form['UserName']
    pwd = request.form['Password']
    print(pwd)
    if not user or not pwd:
        error = "Any of the fields cannot be left blank"
        return redirect(url_for('index', name=error))
    if user != "admin":
        error = "UserName is incorrect!"
        return redirect(url_for('index', name=error))

    else:
        if pwd == "thisispassword":
            return redirect(url_for('addcourses'))
        else:
            error = "Password is incorrect!"
            return redirect(url_for('index', name=error))


@soft.route('/validcourse',methods= ["Post","Get"])
def validcourse():
    if request.method == 'POST':
        try:
            Course = request.form['CourseId']
            Name = request.form['CourseName']
            FID = request.form['FID']
            conn = sqlite3.connect('DATABASE.sqlite')
            c = conn.cursor()
            c.execute("INSERT INTO CourseTable (CourseId, CourseName) VALUES(?, ?)",(Course,Name))
            conn.commit()
            msg = "Recorded Updated sucessfully"
        except:
            conn.rollback()
            msg = "Error updating record"
        return redirect(url_for('addcourses', name=msg))


@soft.route('/addcourses')
@soft.route('/addcourses/<name>')
def addcourses(name=None):
    return render_template("addcourses.html",text=name)


@soft.route('/forgotpassword')
def forgotpassword():
    error = "Contact system administrator"
    return redirect(url_for('index', name=error))


if __name__ == '__main__':
    soft.run(debug=True,port=5500)
