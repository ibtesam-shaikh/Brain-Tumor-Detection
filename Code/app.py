import os
from unittest import result
import tensorflow as tf
import numpy as np
from keras.preprocessing import image
from PIL import Image
import cv2
from keras.models import load_model
from flask import Flask, redirect, request, render_template, session, jsonify
from werkzeug.utils import secure_filename
import mysql.connector 
from sqlite3 import Cursor


app = Flask(__name__)


model =load_model('BrainTumor10Epochs.h5')
print('Model loaded. Check http://127.0.0.1:5000/')

conn = mysql.connector.connect(host="localhost",user="root",password="",database="project")
cursor  = conn.cursor()


def get_className(classNo):
	if classNo==0:
		return "No Brain Tumor"
	elif classNo==1:
		return "Yes Brain Tumor"


def getResult(img):
    image=cv2.imread(img)
    image = Image.fromarray(image, 'RGB')
    image = image.resize((64, 64))
    image=np.array(image)
    input_img = np.expand_dims(image, axis=0)
    result=model.predict(input_img)
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_validation', methods=['POST','GET'])
def login_validation():

    if request.method == "POST":
        user = request.form['username']
        passwd=request.form['password']
    
        cursor.execute("""select * from signup where username LIKE '{}' AND password LIKE '{}'""".format(user,passwd))
        
        signup = cursor.fetchall()
        
        if len(signup) > 0:
            return redirect('/last')       
        else:
            return redirect('/login')
        
        
    
    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    
    if request.method == 'POST':
            firstname = request.form['fname']
            lastname = request.form['lname']
            phonenumber = request.form['phone']
            page = request.form['age']
            emailadd = request.form['mail']
            user = request.form['username']
            passwd = request.form['password']

            cursor.execute("""insert into `signup` (`firstname`,`lastname`,`phone`,`age`,`email`,`username`,`password`) values ('{}','{}','{}','{}','{}','{}','{}')""".format(firstname,lastname,phonenumber,page,emailadd,user,passwd))
            conn.commit()
            return render_template('login.html')
    return render_template('signup.html')

@app.route('/last', methods=['POST','GET'])
def last():
    # if request.method == 'POST':
    #     insert = request.form['checkboxvalue'] 
        
    #     cursor.execute("INSERT INTO symptom (symptoms) VALUES (%s)",[insert])
    #     conn.commit()
    #     cursor.close()
        return render_template('last.html')
    


@app.route('/predict', methods=['POST','GET'])
def upload():
    if request.method == 'POST': 
        
        f = request.files['file']

        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        value=getResult(file_path)
        result=get_className(value) 
        return result
    return None


if __name__ == '__main__':
    app.run(debug=True)