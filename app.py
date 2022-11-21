from flask import Flask, request, render_template, redirect
import pickle

from flask_mysqldb import MySQL

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Float,Integer,String,DateTime
#from flask_migrate import Migrate
#from flask_login import UserMixin, LoginManager, login_user,logout_user, login_required, current_user

#from flask_wtf import FlaskForm
#from wtforms import StringField, IntegerField, FloatField, SubmitField
#from wtforms.validators import DataRequired

from werkzeug.security import generate_password_hash, check_password_hash
import os

import numpy as np

from datetime import datetime
import pytz

#import flask_monitoringdashboard as dashboard



app = Flask(__name__)




#-----------------------------------------Connection Database-----------------------------------------
# MySQL DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/predicts'
                                        
# initialize the database
db = SQLAlchemy(app)
#migrate = Migrate(app, db)

# create BD predict
class Predict(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    total_day_charge = db.Column(db.Float, nullable=False)
    number_customer_service_calls = db.Column(db.Integer, nullable=False)
    total_eve_charge = db.Column(db.Float, nullable=False)
    states = db.Column(db.String(2), nullable=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    output = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Europe/Paris')))


#-----------------------------------------upload prediction model-----------------------------------------
# upload prediction model
model = pickle.load(open('model_states.pkl', 'rb'))

@app.route("/")
def home():
    return render_template('home.html')


# upload prediction model
@app.route('/predict',methods=['GET','POST'])
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
                    #user_id = current_user.id # current_user function
                    )
        
        # add les données dans la BD
        db.session.add(predict)
        db.session.commit()

        if output == 0:
            return render_template('index.html', states=states, prediction_text=f'Un total day charge avec {total_day_charge} , number_customer_service_calls {number_customer_service_calls} , total_eve_charge {total_eve_charge} et state {state} : "no risk of churn"')
        else :
            return render_template('index.html', states=states, prediction_text=f'Un total day charge avec {total_day_charge} , number_customer_service_calls {number_customer_service_calls} , total_eve_charge {total_eve_charge} et state {state} : "risk of churn"')

@app.route('/resultat', methods=['GET','POST'])
#@login_required 
def resultat():
    if request.method == 'GET':
        # get all data with list format
        predicts = Predict.query.all() # take all the data
        #predicts = Predict.query.filter_by(id=current_user.id).all() # filtre only current user data
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



if __name__ == "__main__":
    app.run(debug=True)

# https://www.youtube.com/watch?v=2LqrfEzuIMk


# deactivate under churn-app/venv
# actiavet under churn-app/venv/Scripts