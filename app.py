from flask import Flask, request, render_template, redirect, flash, Response
import pickle
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Float,Integer,String,DateTime
#from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user,logout_user, login_required, current_user

import os
import numpy as np
from datetime import datetime
import pytz

from webforms import LoginForm, UserForm

import flask_monitoringdashboard as dashboard
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)



# flask monitoring dashboard
dashboard.bind(app)



#-----------------------------------------Connection Database-----------------------------------------
# MySQL DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/predicts'

# encode session info with secret key
app.config['SECRET_KEY'] = '\x07\xb0\xd5\xd8+\xc4+\x8aa\x06A\x80_\xc5\xdc\xbb>\xfb\xb9\xe8(\xcf[\x15'

# initialize the database
db = SQLAlchemy(app)
#migrate = Migrate(app, db)

# associate login function and login manager
login_manager = LoginManager()
login_manager.init_app(app)
# login_view = redirect to 'login'
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# create home page
@app.route('/', methods=['GET','POST'])
def home():
    return render_template('home.html')



# create login page
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login succesfull")
                return redirect('/user_dashboard')
            else:
                flash("Password incorrect")
        else:
            flash("That user doesn't exist. Please tray again")
    return render_template('login.html', form=form)

# create logout page
@app.route('/logout', methods=['GET','POST'])
@login_required # access only to login user
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect('/login')

# create user dashboard page
@app.route('/user_dashboard', methods=['GET','POST'])
@login_required
def user_dashboard():
    return render_template('user_dashboard.html')





# create BD predict
class Predict(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    total_day_charge = db.Column(db.Float, nullable=False)
    number_customer_service_calls = db.Column(db.Integer, nullable=False)
    total_eve_charge = db.Column(db.Float, nullable=False)
    states = db.Column(db.String(2), nullable=False)
    # foreign key to link Users (refer to primary key of the user)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    output = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Europe/Paris')))
    


#----------------------------------------- User class -----------------------------------------
# create BD user
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    # User can have Many prédictions
    predict = db.relationship('Predict', backref='user', lazy=True) # associer avec foreign key
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Europe/Paris')))

    @property
    def password(self):
        raise AttributeError('password is not a readable')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create a string
    def __repr__(self):
        return '<name %r>' % self.name



#----------------------------------------- Role class -----------------------------------------



# register
@app.route('/user/add',methods=['GET', 'POST'])
def add_user():
    name = None
    username = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        user1 = Users.query.filter_by(username=form.username.data).first()
        if user1 is None:
            if user is None:
                # hash the password
                hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
                user = Users(username=form.username.data, name=form.name.data, email=form.email.data, password_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
            
                name = form.name.data
                form.name.data = ''
                form.username.data = ''
                form.email.data = ''
                form.password_hash.data = ''
                flash("User added successfully")
            else:
                flash("Email has exist. Please try with another email")
        else:
            flash("Username exist. Please try another username")
    our_users = Users.query.order_by(Users.created_at)
  
    return render_template('register.html',
            form=form,
            name=name,
            username=username,
            our_users=our_users
            )

# update database record
@app.route("/update/<int:id>",methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html",
            form=form,
            name_to_update = name_to_update)
        except:
            flash("Error...Please try again later.")
            return render_template("update.html",
            form=form,
            name_to_update = name_to_update)
    else:
        return render_template("update.html",
            form=form,
            name_to_update = name_to_update,
            id=id)


# delete database record
@app.route("/delete_user/<int:id>",methods=['GET', 'POST'])
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted Successfully!")
        our_users = Users.query.order_by(Users.created_at)
        return render_template("add_user.html",
            form=form,
            name = name,
            our_users= our_users)

    except:
        flash("Error...Please try again later.")
        return render_template("add_user.html",
            form=form,
            name = name,
            our_users= our_users)



#-----------------------------------------upload prediction model-----------------------------------------
# upload prediction model
model = pickle.load(open('model_states.pkl', 'rb'))







# upload prediction model
@app.route('/predict',methods=['GET','POST'])
@login_required
def predict():
    states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
        'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
        'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
        'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
        'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    #predict_array = np.zeros(69)
    predict_array = np.zeros(54)
    idx = 0


    if request.method == 'GET':
        return render_template('index.html',states=states)
    else:

        total_day_charge = float(request.form["total_day_charge"])
        number_customer_service_calls = int(request.form["number_customer_service_calls"])
        total_eve_charge = float(request.form["total_eve_charge"])

        state = request.form["states"]
        predict_array[0] = total_day_charge
        predict_array[1] = number_customer_service_calls
        predict_array[2] = total_eve_charge

        for index, item in enumerate(states):
            if item == state:
                idx = index
        idx = idx + 3
        predict_array[idx] = 1

        #prediction = model.predict([[total_day_charge, number_customer_service_calls,total_eve_charge]])  
        prediction = model.predict([predict_array])  
        output = round(prediction[0], 2) 

        # assigner les données remplit dans le form à la BD
        predict = Predict(total_day_charge=total_day_charge,
                    number_customer_service_calls=number_customer_service_calls,
                    total_eve_charge=total_eve_charge,
                    states=state,
                    output=int.from_bytes(output, "little"),
                    user_id = current_user.id # current_user function
                    )
        
        # add les données dans la BD
        db.session.add(predict)
        db.session.commit()

        if output == 0:
            return render_template('index.html', states=states, prediction_text=f'Un total day charge avec {total_day_charge} , number_customer_service_calls {number_customer_service_calls} , total_eve_charge {total_eve_charge} et state {state} : "no risk of churn"')
        else :
            return render_template('index.html', states=states, prediction_text=f'Un total day charge avec {total_day_charge} , number_customer_service_calls {number_customer_service_calls} , total_eve_charge {total_eve_charge} et state {state} : "risk of churn"')

@app.route('/resultat', methods=['GET','POST'])
@login_required 
def resultat():
    if request.method == 'GET':
        # get all data with list format
        #predicts = Predict.query.all() # take all the data
        predicts = Predict.query.filter_by(user_id = current_user.id).all() # filtre only current user data
        print("test",predicts)
    return render_template('resultats.html', predicts=predicts)



# delete a resultat
@app.route('/<int:id>/delete', methods=['GET'])
#@login_required 
def delete(id):
    predict_delete = Predict.query.get_or_404(id)

    try:
        db.session.delete(predict_delete)
        db.session.commit()
        #flash("Résultat deleted successfully")
        return redirect('/resultat')
    except:
        #flash("There was a problem deleting resultat, please try it later.")
        return redirect('/resultat')





# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500


# flask admin
# class MyModelView(ModelView):
    # is_accessible True = admin is visible by a user
#     def is_accessible(self):
#         return current_user.is_authenticated


# admin = Admin(app)

# admin.add_view(MyModelView(Users, db.session))
# admin.add_view(MyModelView(Predict, db.session))

@app.route('/admins/user', methods=['GET','POST'])
@login_required 
def admin_user():
    name = None
    form = UserForm()
    if request.method == 'GET':
        #id = current_user.id
        email = current_user.email
        if email == 'admin@test.fr':
            our_users = Users.query.order_by(Users.created_at)
            return render_template('admin_user.html',
                form=form,
                name = name,
                our_users= our_users)
        else:
            flash('You are not authorised to visit admin page')
            return render_template('user_dashboard.html')


@app.route('/admins/resultat', methods=['GET','POST'])
@login_required 
def admin_resultat():
    #name = None
    #form = UserForm()
    if request.method == 'GET':
        #id = current_user.id
        email = current_user.email
        predicts = Predict.query.all()
        if email == 'admin@test.fr':
            #our_users = Users.query.order_by(Users.created_at)
            return render_template('resultats.html', predicts=predicts)
        else:
            flash('You are not authorised to visit admin page')
            return render_template('user_dashboard.html')




from logging.handlers import SMTPHandler
from logging import FileHandler, WARNING, ERROR, CRITICAL, INFO, Formatter

file_handler = FileHandler('logs/errorlog.txt')
file_handler.setLevel(ERROR)

app.logger.addHandler(file_handler)

mail_handler = SMTPHandler(
     mailhost=('127.0.0.1', 1025),
     fromaddr='server-error@test.com',
     toaddrs=['admin@test.localhost'],
     subject='Application Error'
  )
mail_handler.setLevel(ERROR)
mail_handler.setFormatter(Formatter(
     '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
     ))

app.logger.addHandler(mail_handler)

@app.route("/log")
def log():
    app.logger.debug('debug')
    app.logger.info('info')
    app.logger.warning('message')
    app.logger.error('error')
    app.logger.critical('critical')
    #return render_template('home.html')
    return Response("test", status=200, mimetype='text/html')

# https://qiita.com/k_future/items/d74b1a26cd9efee8315d
# https://www.youtube.com/watch?v=Ns2baWEoVFg
# https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/logging.html

if __name__ == "__main__":
    app.run(debug=True)

# https://www.youtube.com/watch?v=2LqrfEzuIMk


# deactivate under churn-app/venv
# actiavet under churn-app/venv/Scripts