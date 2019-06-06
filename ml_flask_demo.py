####################################
# Date: 4-9-2019
# Author: Jason Eisele
# Email : jason.eisele@daimler.com
# Modified by : Alex Buettner
# Modifier Email : alex.buettner93@gmail.com

####################################

import numpy as np
from flask import Flask, render_template, flash, request, abort, jsonify, url_for, session, redirect
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import bcrypt
import pickle
from flask_pymongo import PyMongo



my_random_forest = pickle.load(open("iris_rfc.pkl", 'rb'))

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config["MONGO_URI"] = "mongodb://localhost:27017/flaskdb"
mongo = PyMongo(app)


# class ReusableForm(Form):
#     name = TextField('Name:', validators=[validators.DataRequired()])
#     email = TextField('Email:', validators=[validators.DataRequired(), validators.Length(min=6, max=35)])
#     password = TextField('Password:', validators=[validators.DataRequired(), validators.Length(min=3, max=35)])
    
# @app.route("/form", methods=['GET', 'POST'])
# def login_form():
#     form = ReusableForm(request.form)

#     print(form.errors)
#     if request.method == 'POST':
#         name=request.form['name']
#         password=request.form['password']
#         email=request.form['email']
#         print(name, " ", email, " ", password)

#     if form.validate():
#     # Save the comment here.
#         flash('Thanks for registering ' + name)
#     else:
#         flash('Error: All the form fields are required. ')

#     return render_template('register.html', form=form)



@app.route('/')
def index():
    if ('username' in session) and ('active' in session):
        return render_template('home.html', username=session['username'])
#         return 'You are logged in as ' + session['username']

    return render_template('home.html', username = "")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if 'username' in session:
            logout()
        users = mongo.db.users
        login_user = users.find_one({'username' : request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
                users.update({'username' : request.form['username']}, {'$set': { 'active' : True  }})
                session['username'] = request.form['username']
                session['active'] = True
                return redirect(url_for('index'))

        return 'Invalid username/password combination'
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'username' : request.form['username'], 'password' : hashpass, 'active': True})
            session['username'] = request.form['username']
            session['active'] = True
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    if ('username' in session) and ('active' in session):
        users = mongo.db.users
        current_user = session['username']
        users.update({'username':current_user}, {'$set' : { 'active' : False  }})
        session.clear()
    return redirect(url_for('index'))
        

@app.route('/mongo')
def mongo_test():
    if 'username' in session:
        online_users = mongo.db.users.find({'active': True})
        user_list = [doc['username'] for doc in online_users]
        print(user_list)
        return render_template("active_user_list.html",
            names=user_list)
    return render_template("active_user_list.html")

@app.route('/ml_api', methods = ['GET','POST'])
def make_predict(data_in = None):
    if request.method == 'GET':
        return home()
    else:
        if data_in != None:
            predict_request = np.array(data_in)
        else:
        #######all kinds of error checking should go here#######
            data = request.get_json(force = True)
            #Parse our request json into a list of values
            predict_request = [data['sl'], data['sw'], data['pl'], data['pw']]
    #         print(predict_request)
            #Convert our list to a numpy array
            predict_request = np.array(predict_request)
#         print(predict_request)
        #Reshape into 1d array
        predict_request = np.transpose(predict_request).reshape(-1, 4)
        #Assign prediction value to y_hat
        y_hat = my_random_forest.predict(predict_request)
        print(y_hat)
        if data_in != None:
            return np.array(["Setosa","Versicolour","Virginica"])[y_hat][0]
        #Return our prediction to the user
        output = {'y_hat': str(list(y_hat[:]))}
        return  jsonify(results = output)

class PredictForm(Form):
    sl = TextField('Sepal Length:')#, validators=[validators.NumberRange(min=0, max=10)])
    
    sw = TextField('Sepal Width:')#, validators=[validators.DataRequired()])
    
    pl = TextField('Petal Length:')#, validators=[validators.DataRequired()])
    
    pw = TextField('Petal Width:')#, validators=[validators.DataRequired()])
   
    submit = SubmitField("Predict")


@app.route("/predict", methods=['GET', 'POST'])
def predict_form():
    form = PredictForm(request.form)

    print("Form Errors:", form.errors)
    if request.method == 'POST':        
        sl=request.form['sepal_length']
        sw=request.form['sepal_width']
        pl=request.form['petal_length']
        pw=request.form['petal_width']
        
        print("Data from the forms", float(sl),sw,pl,pw)

    if form.validate():
        print("form validated")
        try:
            result = make_predict([float(sl),float(sw),float(pl),float(pw)])
            print("Result", result)
            flash('Identified as: Iris-{}'.format(result))
        except:
            flash('Model Ready. Waiting for values...')
    # Save the comment here.
#         flash('Values in range. {}'.format(""))
    else:
        print(form.errors)
        flash('Error: All the form fields are required to be numbers between 0.0 and 10.0')

    return render_template('data_input.html', form=form)    
if __name__ == '__main__':
    app.run(port = 9000, debug = True, use_reloader=True)
