import pickle
import secrets
import joblib
import OpenSSL
import numpy as np
import sklearn
from flask import Flask, flash, render_template, request,redirect,url_for
import pymongo
# from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


#------------------------------------ DB CONNECTIVITY -------------------------------

# client = pymongo.MongoClient("mongodb+srv://rdharun:Rdharun@cluster0.0xnuof7.mongodb.net/?retryWrites=true&w=majority")
# db = client.CRV


client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['CRV']


#--------------------------------------- DRIVER CODE ---------------------------------

app = Flask(__name__)
model = pickle.load(open("vot_reg.pkl", "rb"))

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/y_register',methods=['GET','POST'])
def y_register():
    if request.method == "POST":
        # Get the user data from the form
        name = request.form.get("name")
        print(name)
        username = request.form.get("username")
        print(username)
        password = request.form.get("password")
        print(password)

        # salt = secrets.token_hex(16)
        # print(salt)

        hashed_password = generate_password_hash(password)
        print(hashed_password)
        
        # Check if the username is already taken
        existing_user = db.UserLogin.find_one({"username": username})
        if existing_user:
            return render_template('register.html',message='Username already exists ...!!')
        
        # Insert the new user into the database
        rec = {"name":name,"username":username,"password":hashed_password}
        db.UserLogin.insert_one(rec)
        
        return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/y_login',methods=['GET','POST'])
def y_login():
        if request.method == "POST":
        # Get the user data from the form
            username = request.form.get("username")
            password = request.form.get("password")
        
        user = db.UserLogin.find_one({"username": username})
        stored_pass = user['password']
        print("stored pass")
        print(stored_pass)

        check_pass = check_password_hash(stored_pass,password)
        print(check_pass)
        if (check_password_hash(stored_pass, password)):
            # Login successful
            return redirect(url_for('home'))
        else:
            # Login failed
            return render_template('login.html',message='Invalid Credentials ...!!!')



@app.route('/home')
def home():
    return render_template('resaleintro.html')


@app.route('/predict')
def predict():
    return render_template('prediction.html')

@app.route('/y_predict',methods=['GET','POST'])
def y_predict():

    Fuel_Type_Diesel=0
    
    if request.method == 'POST':
        Name = request.form['car_name']
        Year = int(request.form['Year'])
        Present_Price=float(request.form['Present_Price'])
        Kms_Driven=int(request.form['Kms_Driven'])
        Owner=int(request.form['Owner'])
        Fuel_Type=request.form['Fuel_Type']
        if(Fuel_Type=="Petrol"):
                Fuel_Type_Petrol=1
                Fuel_Type_Diesel=0
                Fuel_Type_Cng=0
        elif(Fuel_Type=="Diesel"):
                Fuel_Type_Diesel=1
                Fuel_Type_Petrol=0
                Fuel_Type_Cng=0
        else:
            Fuel_Type_Cng=1
            Fuel_Type_Petrol=0
            Fuel_Type_Diesel=0

        Year=2023-Year
        Seller_Type_Individual=request.form['Seller_Type']
        if(Seller_Type_Individual=='Individual'):
            Seller_Type_Individual=1
        else:
            Seller_Type_Individual=0
        Transmission_Mannual=request.form['Transmission']
        if(Transmission_Mannual=='Manual'):
            Transmission_Mannual=1
        else:
            Transmission_Mannual=0
        
        print(request.form)

        prediction=model.predict(np.array([[Present_Price, 
                                            Kms_Driven, 
                                            Owner,
                                            Year,
                                            Fuel_Type_Cng, 
                                            Fuel_Type_Diesel, 
                                            Fuel_Type_Petrol, 
                                            Seller_Type_Individual, 
                                            Transmission_Mannual]]))

        output=round(prediction[0],2)
        if output<0:
            return render_template('prediction.html',prediction_texts="Sorry you cannot sell this car")
        else:
            return render_template('prediction.html',prediction_texts="You can sell the Car at Rs. {}".format(output))
    else:
        return render_template('prediction.html')
    
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/y_contact',methods=['GET','POST'])
def y_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        msg = request.form['message']

    rec = {"NAME":name,"EMAIL":email,"MESSAGE":msg}
    db.UserMessage.insert_one(rec)
    return render_template('contact.html',message='Message sent !!!')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__=="__main__":
    app.run(debug=True)
