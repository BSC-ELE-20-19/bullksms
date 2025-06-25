##THIS WLL HAVE ALL THE LINKS TO THE DIFFIRENT PAGES
from flask import Flask, Blueprint, render_template, jsonify, redirect, request, session, Response,stream_with_context,url_for,send_file,flash
import re
import sys
import os
from send_sms import sending
import pandas as pd

#import mysql.connector



app=Flask(__name__)

views= Blueprint('views', __name__)


@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/admin')
def admin():
    return render_template('home.html')

@app.route('/go_to_log')
def go_to_log():
    return render_template('activated.html')

@app.route('/go_to_home')
def go_to_home():
    return render_template('changed.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST': #CHECKING IF ITS A POST
        username= request.form.get('authorised_username') #GETTING USER INPUT DATA FROM THE FIELDS UPON SUBMIT
        password= request.form.get('authorised_password')
      
        if username=="ACADES" and password=="Acades123456":
            response =redirect(url_for('admin'))
            return response
          #IF USER CREDENTIALS MATCH GO TO HOME
        else:
            alert="Incorrect username or password"
            return render_template('login.html', error_message=alert)
    return render_template('login.html')


@app.route('/logout_admin')
def logout_admin():
    response =redirect(url_for('home'))
    response.set_cookie('session','',expires=0,httponly=True,secure=True,samesite='Lax')
    return response


@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/profile')
def profile():
    username="ACADES"
    return render_template('profile.html', username=username)


@app.route('/send', methods=['GET', 'POST'])
def send():
    username="ACADES"
    return render_template('bulksms.html', username=username)


@app.route('/send_sms', methods=['POST', 'GET'])
def send_SMS():
    file = request.files['excel_file']
    message=request.form['message'] 
    df = pd.read_excel(file)
    df['phone'] = df['phone'].apply(lambda x: '+' + str(x) if not str(x).startswith('+') else str(x))
    recipients = df['phone'].tolist()
    if 'phone' not in df.columns:
        return "Excel must have a column named 'phone'", 400
    
    sending(message,recipients) 
    print(f"Sending: {message}")
    return 'sms sent successfully'
    


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__== '__main__':
   app.run( host='0.0.0.0',port=5000,debug=True,use_reloader=False)