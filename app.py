from flask import Flask, redirect, url_for, request,render_template,session
app = Flask(__name__)
import smtplib
import sqlite3
import binascii
from Crypto.Cipher import AES
sqlite_file='DATABASE.sqlite'
global globalFID
app.secret_key = 'thisisdatabase'

def encrypt(s):
    obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    s1=s.rjust(16,',')
    u=obj.encrypt(s1)
    bar=binascii.b2a_hex(u)
    return bar


def decryption(s):
    obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    u=binascii.a2b_hex(s)
    u1=obj.decrypt(u)
    ux=u1.strip(',')
    return ux


@app.route('/')
@app.route('/<name>')
def index(name=None):
    return render_template('HomePage.html',session=session,text=name)


@app.route('/success/<name>')
def success(name):
    return name

@app.route('/signuppage')
def signuppage():
   return render_template('SignUp.html')

@app.route('/forgotpassword')
@app.route('/forgotpassword/<name>')
def forgotpassword(name=None):
   return render_template('Forgot.html',text=name)


@app.route('/login',methods = ['POST', 'GET'])
def login():
    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    SIDtopass = 0
    person = request.form.get('person','')
    user1 = request.form['UserName']
    user=encrypt(user1)
    print user
    pwd1 = request.form['Password']
    pwd=encrypt(pwd1)
    print pwd
    #validate if all fields are entered
    if not person or not user or not pwd:
        error = "Any of the fields cannot be left blank"
        return redirect(url_for('index', name=error))
    if person == 'Student':
        c.execute("select Password from StudentLoginTable where UserName = ?",(user,))
        f = c.fetchall()
        if not f:
            error = "UserName is incorrect!"
            return redirect(url_for('index', name=error))

        for row in f:
            if row == (pwd,):
                c.execute("select SID from StudentLoginTable where UserName = ?",(user,))
                f = c.fetchone() # this is SID to be passed
                #return redirect(url_for('success', name=f))
                session['id']=f;
                con = sqlite3.connect('DATABASE.sqlite')
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                sid = session['id']
                cur.execute("SELECT StudentName as sn FROM StudentLoginTable WHERE SID=?", sid)
                sname1 = cur.fetchone()
                con1 = sqlite3.connect('DATABASE.sqlite')
                con1.create_function('decryption', 1, decryption)
                con1.row_factory = sqlite3.Row
                cur1 = con1.cursor()
                cur1.execute(
                    "SELECT c.CourseName as cn,decryption(g.MidTerm1) as mt1,decryption(g.MidTerm2) as mt2,decryption(g.MidTerm3) as mt3,decryption(g.FinalGrade) as fg FROM GradeTable g Inner Join CourseTable c on g.CourseId=c.CourseId WHERE g.SID=?",
                    sid)
                rows = cur1.fetchall()
                return render_template('StudentGrades.html',sname=sname1,rows=rows)

            else:
                error = "Password is incorrect!"
                return redirect(url_for('index', name=error))
    elif person == 'Faculty':
        c.execute("select Password from FacultyLoginTable where UserName = ?", (user,))
        f = c.fetchall()
        if not f:
            error = "UserName is incorrect!"
            return redirect(url_for('index', name=error))
        for row in f:
            print row
            print pwd
            if row == (pwd,):
                c.execute("select FID from FacultyLoginTable where UserName = ?", (user,))
                f = c.fetchone() #this is FID to be passed
                #return redirect(url_for('success', name=f))
                global globalFID
                globalFID = f
                session['id']=f
                fid = session['id']
                con = sqlite3.connect('DATABASE.sqlite')
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute("SELECT FacultyName as fn FROM FacultyLoginTable WHERE FID=?", fid)
                sname2 = cur.fetchone()
                print sname2
                con1 = sqlite3.connect('DATABASE.sqlite')
                con1.create_function('decryption',1,decryption)
                con1.row_factory = sqlite3.Row
                cur1 = con1.cursor()
                cur1.execute(
                    "SELECT s.StudentName as sn,g.SID as sid,g.CourseId as crid,decryption(g.MidTerm1) as mt1,decryption(g.MidTerm2) as mt2,decryption(g.MidTerm3) as mt3,decryption(g.FinalGrade) as fg FROM GradeTable g Inner Join StudentLoginTable s on g.SID=S.SID WHERE g.FID=?",
                    fid)
                rows2 = cur1.fetchall()
                for i in rows2:
                    print i
                return render_template('Instructormodule.html', sname=sname2, rows=rows2,link=None)

            else:
                error = "Password is incorrect!"
                return redirect(url_for('index', name=error))


@app.route('/facultylogindisplay/<fidvalue>')
def facultylogindisplay(fidvalue):
    session['id'] = fidvalue
    con = sqlite3.connect('DATABASE.sqlite')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    print(fidvalue)
    fi = int(fidvalue[0])
    cur.execute("SELECT FacultyName as fn FROM FacultyLoginTable WHERE FID=?", fi)
    sname2 = cur.fetchone()
    con1 = sqlite3.connect('DATABASE.sqlite')
    con1.row_factory = sqlite3.Row
    cur1 = con1.cursor()
    cur1.execute(
        "SELECT s.StudentName as sn,g.SID as sid,g.CourseId as crid,g.MidTerm1 as mt1,g.MidTerm2 as mt2,g.MidTerm3 as mt3,g.FinalGrade as fg FROM GradeTable g Inner Join StudentLoginTable s on g.SID=S.SID WHERE g.FID=?",
        fi)
    rows2 = cur1.fetchall()
    return render_template('Instructormodule.html', sname=sname2, rows=rows2,a=None,b=None,c=None)


@app.route('/forgothandling',methods = ['POST', 'GET'])
def forgothandling():
    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)
    conn.create_function('decryption',1,decryption)
    c = conn.cursor()
    email = request.form['Email']
    person = request.form.get('person', '')

    if not email or not person:
        error = "Any of the fields cannot be left blank"
        return redirect(url_for('forgotpassword', name=error))

    if person == 'Student':
        c.execute("select decryption(Password) from StudentLoginTable where email = ?", (email,))
        f = c.fetchone()
        if not f:
            error = "Email entered is incorrect!"
            return redirect(url_for('forgotpassword', name=error))
        else:
            to = email
            gmail_user = 'studentacademyportal@gmail.com'
            gmail_pwd = 'hellostudent'
            smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo()  # extra characters to permit edit
            smtpserver.login(gmail_user, gmail_pwd)
            header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:Confidential Message \n'
            print
            header
            msg = header + '\n This message contains your password to Student Academic Portal \n\n' + str(f[0])
            smtpserver.sendmail(gmail_user, to, msg)
            print
            'done!'
            smtpserver.quit()
        message = "An Email containing password has been sent to your registered email ID"
        return redirect(url_for('forgotpassword', name=message))
    elif person == 'Faculty':
        c.execute("select decryption(Password) from FacultyLoginTable where Email = ?", (email,))
        f = c.fetchall()
        if not f:
            error = "Email entered is incorrect!"
            return redirect(url_for('forgotpassword', name=error))
        else:
            to = email
            gmail_user = 'studentacademyportal@gmail.com'
            gmail_pwd = 'hellostudent'
            smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo()  # extra characters to permit edit
            smtpserver.login(gmail_user, gmail_pwd)
            header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:Confidential Message \n'
            print
            header
            msg = header + '\n This message contains your password to Student Academic Portal \n\n' + str(f)
            smtpserver.sendmail(gmail_user, to, msg)
            print
            'done!'
            smtpserver.quit()
            message = "An Email containing password has been sent to your registered email ID"
            return redirect(url_for('forgotpassword', name=message))


@app.route('/updategrades', methods=['GET', 'POST'])
def updategrades():
    connection = sqlite3.connect(sqlite_file)
    cr = connection.cursor()
    cid=request.form.get('CourseId',0)
    sid=request.form.get('StudentId',0)
    mt1x=request.form.get('MidTerm1',0)
    mt1=encrypt(mt1x)
    mt2x=request.form.get('MidTerm2',0)
    mt2 = encrypt(mt2x)
    mt3x=request.form.get('MidTerm3',0)
    mt3 = encrypt(mt3x)
    fgx=request.form.get('FinalGrades','A')
    fg = encrypt(fgx)
    global globalSID
    global globalFID
    task = (mt1, mt2, mt3, fg, sid, globalFID[0], cid)
    sql = "update GradeTable set MidTerm1 = ?, MidTerm2 = ?, MidTerm3 = ?, FinalGrade = ? where SID = ? and FID = ? and CourseId = ?"
    cr.execute(sql,task)
    a = cr.rowcount
    if a == 0:
        return 'The student didnot register the course'
    else:
    # commit and close connection
        connection.commit()
        connection.close()
        con = sqlite3.connect('DATABASE.sqlite')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        print(globalFID)
        print(cid)
        print(session['id'])
        z = session['id']
        cur.execute("SELECT FacultyName as aa FROM FacultyLoginTable WHERE FID=?", z)
        sname2 = cur.fetchone()
        print sname2
        con1 = sqlite3.connect('DATABASE.sqlite')
        con1.create_function('decryption', 1, decryption)
        con1.row_factory = sqlite3.Row
        cur1 = con1.cursor()
        cur1.execute(
        "SELECT s.StudentName as sn,g.SID as sid,g.CourseId as crid,decryption(g.MidTerm1) as mt1,decryption(g.MidTerm2) as mt2,decryption(g.MidTerm3) as mt3,decryption(g.FinalGrade) as fg FROM GradeTable g Inner Join StudentLoginTable s on g.SID=S.SID WHERE g.FID=?",
        z)
        rows2 = cur1.fetchall()
        for i in rows2:
            print i
        return render_template('Instructormodule.html', sname=sname2, rows=rows2, link=None)


@app.route('/callhtml/<a>/<b>/<c>/<d>/<e>' , methods=['GET', 'POST'])
def callhtml(a,b,c,d,e):
    return render_template('update.html',a=a,b=b,c=c,d=d,e=e)


@app.route('/clear')
def clearsession():
    # Clear the session
    session.clear()
    # Redirect the user to the main page
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    name = request.form['Name']
    person = request.form.get('person', '')
    user1 = request.form['UserName']
    user=encrypt(user1)
    pwd1 = request.form['Password']
    pwd=encrypt(pwd1)
    email = request.form['email']

    # validate if all fields are entered
    if not person or not user or not pwd or not email or not name:
        error = "Any of the fields cannot be left blank"
        return redirect(url_for('success', name=error))

    if person == 'Student':
        c.execute("select UserName from StudentLoginTable")
        f = c.fetchall()
        mark = 0
        for row in f:
            if row == (user,):
                mark = 1
                msg = "User already exists"
                break
        if mark !=1:
            sql = "insert into StudentLoginTable(StudentName, UserName, Password, Email) values(?,?,?,?)"
            i = 1
            values = (name, user, pwd, email)
            c.execute(sql, values)
            msg = "User has been registered successfully"


        # commit and close connection
        conn.commit()
        conn.close()
        return redirect(url_for('success', name=msg))
    elif person == 'Faculty':
        c.execute("select UserName from FacultyLoginTable")
        f = c.fetchall()
        mark = 0
        for row in f:
            if row == (user,):
                mark = 1
                msg = "User already exists"
                break
        if mark != 1:
            sql = "insert into FacultyLoginTable(FacultyName, UserName, Password, Email) values(?,?,?,?)"
            i = 1
            values = (name, user, pwd, email)
            c.execute(sql, values)
            msg = "User has been registered successfully"
        # commit and close connection
        conn.commit()
        conn.close()
        return redirect(url_for('success', name=msg))


if __name__ == '__main__':
    app.run(debug=True)