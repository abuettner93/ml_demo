####################################
# Date: 4-9-2019
# Author: Jason Eisele
# Email : jason.eisele@daimler.com
# Modified by : Alex Buettner
# Modifier Email : alex.buettner93@gmail.com

####################################

import numpy as np
from flask import Flask, render_template, flash, request, abort, jsonify
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import pickle

my_random_forest = pickle.load(open("iris_rfc.pkl", 'rb'))

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


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


  
@app.route('/', methods=['GET'])
def root():
    return home()
    
@app.route('/home', methods = ['GET'])
def home():
    return """
<!DOCTYPE html>
<head>
   <title>Iris Identification Machine Learning Model</title>
   <link rel="stylesheet" href="http://stash.compjour.org/assets/css/foundation.css">
</head>
<body style="width: 880px; margin: auto;">  
    <h1>Iris Dataset Machine Learning Web Service</h1>
    <p>You have reached the Iris machine learning web service. This web API allows you to figure out what kind of flower you have based on some input parameters. So break out the rulers and see what math and science can do.</p>
    <p>And here's an image:</p>
    <a data-flickr-embed="true"  href="https://www.flickr.com/photos/martinlabar/137433273/" title="Blue and white iris"><img src="https://live.staticflickr.com/53/137433273_6bc2fce01c_b.jpg" width="1024" height="768" alt="Blue and white iris"></a><script async src="//embedr.flickr.com/assets/client-code.js" charset="utf-8"></script>
</body>
"""

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

if __name__ == '__main__':
    app.run(port = 9000, debug = True, use_reloader=True)
