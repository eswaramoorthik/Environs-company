from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)

app.secret_key = 'abc@123'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'AZsx@1209'
app.config['MYSQL_DB'] = 'company'

mysql = MySQL(app)

def is_password_storng(password):
    if len(password)<8 :
        return False
    if not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password) or not re.search(r"\d",password):
        return False
    if not re.search(r"[!@#$%^&*()-+{}|\"<>]?", password):
        return False
 
    return True

def isloggedin():
    return 'username' in session

@app.route('/')
def home():
    return render_template('navbar.html')     

class User:
    def __init__(self, id, username, password) :
        self.id = id
        self.username = username
        self.password = password

class signin_form(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired()])     
    submit = SubmitField('Signin')   

class login_form(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=15)])     
    submit = SubmitField('Login')

class add_form(FlaskForm):
    name = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    age = IntegerField('Age', validators=[InputRequired()])
    dept = StringField('Department', validators=[InputRequired(), Length(min=4, max=20)])
    salery =IntegerField('Salery', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])
    submit = SubmitField('Add')

class edit_form(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    age = IntegerField('Age', validators=[InputRequired()])
    dept = StringField('Department', validators=[InputRequired(), Length(min=4, max=20)])
    salery =IntegerField('Salery', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])    
    SubmitField = SubmitField('Edit')

@app.route('/signup/', methods = ['GET', 'POST'])
def signup():
    form = signin_form()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if not is_password_storng(password):
            flash('Password should be 8 character with upper case and lower case and special character', 'danger')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute('select id from signup where name = %s', (username,))
        old_user = cur.fetchone()
        if old_user:
            cur.close()
            flash('Username already taken. Please choose a different one.', 'danger')
            return render_template('signup.html')
        cur.execute('insert into signup (name, password) values  (%s, %s)', (username, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('Signup Successful', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form = form)


@app.route('/login/', methods = ['GET', 'POST'])
def login():
    form = login_form()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute('select id, name, password from signup where name = %s', (username,))
        login_id = cur.fetchone()
        print(login_id)
        cur.close()
        if login_id:
            save_password = login_id[2]
            if check_password_hash(save_password, password):
                user = User(id = login_id[0], username= login_id[1], password= login_id[2])
                session['username'] = user.username           
                return redirect((url_for('table')))
        else:
            flash('Invalid Credentials', 'Danger')
    return render_template('login.html', form = form)

@app.route('/add/', methods = ['GET', 'POST'])
def add():
    form = add_form()
    if form.validate_on_submit():
        username =   form.name.data
        age = form.age.data
        dept = form.dept.data
        salery = form.salery.data
        address = form.address.data
        cur = mysql.connection.cursor()
        cur.execute('insert into employee (name, age, dept, salery, address) values (%s, %s, %s, %s, %s)', (username, age, dept, salery, address))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('table'))
    return render_template('add.html', form = form)     

@app.route('/table/')
def table():
    if isloggedin():
        username = session['username']
        cur = mysql.connection.cursor()
        cur.execute('select * from employee where name = %s', (username,))
        data = cur.fetchall()
        cur.close()
        return render_template('table.html', data=data)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()
    if request.method == 'POST':
        Name =   request.form['username']
        Age = request.form['age']
        Dept = request.form['dept']
        Salery = request.form['salery']
        Address = request.form['address']
        cur = mysql.connection.cursor()
        cur.execute('UPDATE employee SET name = %s, age = %s, dept = %s, salery = %s, address = %s WHERE id = %s', (Name, Age, Dept, Salery, Address, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('table'))
    return render_template('edit1.html', data =data)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def remove(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM employee WHERE id = %s', (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("table"))

@app.route('/logout/')
def logout():
    session.pop('user', None) 
    flash('Logged out seccessfully', 'seccess')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
