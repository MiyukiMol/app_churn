from flask import Flask, request, render_template, redirect
import pickle

from flask_mysqldb import MySQL
import mysql.connector # pip install mysql-connector-python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Float,Integer,String,DateTime
#from flask_login import UserMixin, LoginManager, login_user,logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash
import os

from datetime import datetime
#import pytz

#import flask_monitoringdashboard as dashboard



app = Flask(__name__)


#-----------------------------------------Connection Database-----------------------------------------
def get_user_by_username(username):
    mydb = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd="root",
        database="movie_5"
        )
    mycursor = mydb.cursor()
    #mycursor.execute("SELECT * FROM actor")
    return mydb, mycursor

mydb, mycursor = get_user_by_username("root")

#for x in mycursor:
#    print(x)

try:
    mydb, mycursor = get_user_by_username("root") 
    #mydb = mysql.connector.connect(
                                        #host = "localhost",
                                        #user="root",
                                        #passwd="root",
                                        #database = "movie_5",
                                        #auth_plugin='mysql_native_password',
                                        #)
except:
    print ("I am unable to connect to the database")



#-----------------------------------------upload prediction model-----------------------------------------
# upload prediction model
model = pickle.load(open('model.pkl', 'rb'))

@app.route("/")
def home():
    return render_template('index.html')


# upload prediction model
@app.route('/predict',methods=['GET','POST'])
def predict():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        total_day_charge = float(request.form["total_day_charge"])
        number_customer_service_calls = int(request.form["number_customer_service_calls"])
        total_eve_charge = float(request.form["total_eve_charge"])

        prediction = model.predict([[total_day_charge, number_customer_service_calls,total_eve_charge]])  
        output = round(prediction[0], 2) 

        if output == 0:
            return render_template('index.html', prediction_text=f'Un total day charge avec {total_day_charge} , number_customer_service_calls {number_customer_service_calls} et total_eve_charge {total_eve_charge} : "no risk of churn"')
        else :
            return render_template('index.html', prediction_text=f'Un total day charge avec {total_day_charge} , number_customer_service_calls {number_customer_service_calls} et total_eve_charge {total_eve_charge} : "risk of churn"')




# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500



if __name__ == "__main__":
    app.run(debug=True)

# https://www.youtube.com/watch?v=2LqrfEzuIMk


# desactivate under churn-app/venv
# actiavet under churn-app/venv/Scripts