##THIS FILE CONTAINES ALL THE LOG IN PAGES FOR OUR APP

from flask import Blueprint, render_template, request

auths= Blueprint('auths', __name__)



##WHAT WE ARE DOING HERE IS TO CREATE A URL, THEN CREATE A FUNCTION WHICH WILL DISPLAY A VIEW WHEN THE 
#IS CALLED
##HERE, WE ARE HANDLIND THE METHOD IN login.php BY 

@auths.route('/login', methods=['GET', 'POST']) #CALLING THE REQUEST TYPE HERE
def login():
    if request.method=='POST': #CHECKING IF ITS A POST
        email= request.form.get('email') #GETTING USER INPUT DATA FROM THE FIELDS UPON SUBMIT
        password= request.form.get('Password')
        print("Email",email)
        print("Password", password)
    return render_template("login.html")

@auths.route('/Sign-up', methods=['POST', 'GET'])
def Signup():
    if request.method=='POST':
        email=request.form.get('email')
        firstname=request.form.get('firstname')
        lastname=request.form.get('lastname')
        password=request.form.get('password')
        print("Email",email)
        print("Password", password)
    return render_template("signup.html")
