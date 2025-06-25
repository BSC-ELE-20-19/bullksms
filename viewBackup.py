##THIS WLL HAVE ALL THE LINKS TO THE DIFFIRENT PAGES
from flask import Flask, Blueprint, render_template, jsonify, redirect, request, session, Response,stream_with_context,url_for,send_file,flash
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from fpdf import FPDF
from werkzeug.security import generate_password_hash,check_password_hash,gen_salt
import re
import os
from functools import wraps
#import mysql.connector



app=Flask(__name__)
app.secret_key="locked_hahahaha"
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='mother'
mysql=MySQL(app)


#IF FLASK-MYSQL DB WONT WONT, SETUP USING MYSQL CONNECTOR BELOW
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
#THEN HAVE connection=get_db_connectin()


views= Blueprint('views', __name__)

from create_tables import create_admini_table,create_area_table,create_coordinator_table,create_members_table,create_zone_table


from connect_database import connect_to_database

connection = connect_to_database()
create_admini_table(connection)
create_members_table(connection)
create_area_table(connection)
create_zone_table(connection)
create_coordinator_table(connection)




#AUNTHENTICATION DECORATOR
def login_required_admin(f):
    @wraps(f)
    def decorated_function_admin(*args,**kwargs):
        if 'admin_name' not in session:
            return render_template('login.html')
        return f(*args,**kwargs)
    return decorated_function_admin


def login_required_regi(f):
    @wraps(f)
    def decorated_function_regi(*args,**kwargs):
        if 'agent_name' not in session:
            return render_template('agent_log.html')
        return f(*args,**kwargs)
    return decorated_function_regi




#CALLING HOME PAGE FOR THE SYSTEM
@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/admin')
@login_required_admin
def admin():
    return render_template('home.html')

@app.route('/go_to_log')
def go_to_log():
    return render_template('activated.html')

@app.route('/go_to_home')
@login_required_admin
def go_to_home():
    return render_template('changed.html')

@app.route('/change_pass', methods=['GET','POST'])
@login_required_admin
def create_pass():
    if request.method=='POST': #CHECKING IF ITS A POST
        new_password= request.form.get('user_password') #GETTING USER INPUT DATA FROM THE FIELDS UPON SUBMIT
        verify_password= request.form.get('confirm_password')
        old_password= request.form.get('old_password')
        role= "admin"
        alert=""
        username=session['admin_name']
        
        if new_password !=verify_password:
            alert="Passwords do not match"
            return render_template('change_pass.html', error_message=alert)
        
        elif len(new_password) < 8 or not re.search(r'[A-Z]',new_password) or not re.search(r'[0-9]',new_password):
            alert="Password must have atleast 8 characters long and contain a number and an uppercase letter"
            return render_template('change_pass.html', error_message=alert)
        
        curs=mysql.connect.cursor()
        curs.execute("SELECT admin_id,mypassword FROM admins WHERE username=%s AND role=%s", (username,role,))
        user = curs.fetchone()
        if user and check_password_hash(user[1],old_password):
            session['admin_name']=username
            hashed_password=generate_password_hash(new_password,method='pbkdf2:sha256')
            query=("UPDATE admins SET mypassword=%s WHERE admin_id=%s")
            values= (hashed_password,user[0])
            curs.execute(query, values)
            curs.close()
            response =redirect(url_for('go_to_log'))
            return response
        else:
            alert="Incorrect username or password"
            return render_template('change_pass.html', error_message=alert)
        
    return render_template('change_pass.html')



@app.route('/change_name', methods=['GET','POST'])
@login_required_admin
def change_name():
    if request.method=='POST': #CHECKING IF ITS A POST
        password= request.form.get('user_password') #GETTING USER INPUT DATA FROM THE FIELDS UPON SUBMIT
        new_name= request.form.get('new_name')
        role= "admin"
        alert=""
        username=session['admin_name']
        
        curs=mysql.connect.cursor()
        curs.execute("SELECT admin_id,mypassword FROM admins WHERE username=%s AND role=%s", (username,role,))
        user = curs.fetchone()
        if user and check_password_hash(user[1],password):
            query=("UPDATE admins SET username=%s WHERE admin_id=%s")
            values= (new_name,user[0])
            curs.execute(query, values)
            curs.close()
            session['admin_name']=new_name
            response =redirect(url_for('go_to_home'))
            return response
        else:
            alert="Incorrect username or password"
            return render_template('change_name.html', error_message=alert)
        
    return render_template('change_name.html')



@app.route('/register_admin',methods=['GET', 'POST'])
def register_admin():
    if request.method=='POST': #CHECKING IF ITS A POST
        username= request.form.get('user_username') #GETTING USER INPUT DATA FROM THE FIELDS UPON SUBMIT
        password= request.form.get('user_password')
        confirm_password= request.form.get('confirm_password')
        role= "admin"
        alert=""
        
        if password !=confirm_password:
            alert="Passwords do not match"
            return render_template('register_admin.html', error_message=alert)
        if len(password) < 12 or not re.search(r'[A-Z]',password) or not re.search(r'[0-9]',password):
            alert="Password must have atleast 12 characters long and contain a number and an uppercase letter"
            return render_template('register_admin.html', error_message=alert)
        
        hashed_password=generate_password_hash(password,method='pbkdf2:sha256')
        curs=mysql.connect.cursor()
        curs.execute('INSERT INTO admins(username,mypassword,role) VALUES (%s,%s,%s)',(username,hashed_password,role))
        return render_template('login.html')

    return render_template('register_admin.html')


@app.route('/register_regi',methods=['GET', 'POST'])
@login_required_admin
def register_regi():
    if request.method=='POST': #CHECKING IF ITS A POST
        username_reg= request.form.get('user_username') #GETTING USER INPUT DATA FROM THE FIELDS UPON SUBMIT
        password_reg= request.form.get('user_password')
        confirm_password= request.form.get('confirm_password')
        role= "registrar"
        alert=""
        
        if password_reg !=confirm_password:
            alert="Passwords do not match"
            return render_template('register_regi.html', error_message=alert)
        if len(password_reg) < 8 or not re.search(r'[A-Z]',password_reg) or not re.search(r'[0-9]',password_reg):
            alert="Password must have atleast 8 characters long and contain a number and an uppercase letter"
            return render_template('register_regi.html', error_message=alert)
        hashed_password=generate_password_hash(password_reg,method='pbkdf2:sha256')
        curs=mysql.connect.cursor()
        curs.execute('INSERT INTO admins(username,mypassword,role) VALUES (%s,%s,%s)',(username_reg,hashed_password,role))
        return render_template('agent_log.html')
    return render_template('register_regi.html')
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST': #CHECKING IF ITS A POST
        username= request.form.get('authorised_username') #GETTING USER INPUT DATA FROM THE FIELDS UPON SUBMIT
        password= request.form.get('authorised_password')
        role= "admin"
        alert="Incorrect username or password"
        #connection = get_db_connection()
        curs=mysql.connect.cursor()
        curs.execute("SELECT mypassword FROM admins WHERE username=%s AND role=%s", (username,role,))
        user = curs.fetchone()
        curs.close()
        
        if user and check_password_hash(user[0],password):
            session['admin_name']=username
            response =redirect(url_for('admin'))
            return response
          #IF USER CREDENTIALS MATCH GO TO HOME
        else:
            alert="Incorrect username or password"
            return render_template('login.html', error_message=alert)
    return render_template('login.html')


@app.route('/agent_log', methods=['GET', 'POST'])
def agent_log():
    if request.method=='POST': #CHECKING IF ITS A POST
        username= request.form.get('authorised_username') #GETTING USER INPUT DATA FROM THE FIELDS UPON SUBMIT
        password= request.form.get('authorised_password')
        role= "registrar"
        alert="Incorrect username or password"
        curs=mysql.connect.cursor()
        curs.execute("SELECT mypassword FROM admins WHERE username=%s AND role=%s", (username,role,))
        user_reg = curs.fetchone()
        curs.close()
        
        if user_reg and check_password_hash(user_reg[0],password):
          #IF USER CREDENTIALS MATCH GO TO HOME
            session['agent_name']=username
            response =redirect(url_for('agent_home'))
            return response

        else:
            alert="Incorrect username or password"
            return render_template('agent_log.html', error_message=alert)
    return render_template('agent_log.html')







@app.route('/logout_admin')
def logout_admin():
    session.pop('admin_name',None)
    response =redirect(url_for('login'))
    response.set_cookie('session','',expires=0,httponly=True,secure=True,samesite='Lax')
    return response

@app.route('/logout_agent')
def logout_agent():
    session.pop('agent_name',None)
    response =redirect(url_for('agent_log'))
    response.set_cookie('session','',expires=0,httponly=True,secure=True,samesite='Lax')
    return response




@app.route('/agent_home')
@login_required_regi
def agent_home():
    username=session['agent_name']
    return render_template('agent_home.html',username=username)

@app.route('/register/<int:zone_id>', methods=['GET','POST'])
@login_required_regi
def register(zone_id):
    curs=mysql.connect.cursor()
    curs_area=mysql.connect.cursor()
    query=("SELECT * FROM zoner WHERE zone_id = %s")
    values= (zone_id,)
    curs.execute(query, values)
    zone_name = curs.fetchone()
    if zone_name:
        curs_area.execute("SELECT * FROM areas WHERE zone_id=%s",(zone_id,))
        area_list = curs_area.fetchall()
        zone_na=zone_name[1]
        
    curs.close()
    return render_template('register.html', zone_name=zone_na, area_list=area_list)
    #IF NO NAME PRESENT REDIRECT TO LOG IN PAGE
#LOG IN PAGE

@app.route('/stats')
@login_required_admin
def stats():
    return render_template('stats.html')

@app.route('/profile')
@login_required_admin
def profile():
    username=session['admin_name']
    return render_template('profile.html', username=username)



#RENDERING AREA AND AGENT COORDINATOR PAGE
@app.route('/area_cord')
@login_required_admin
def area_cordinator():
    return render_template('area_cord.html')


@app.route('/zone_cord')
@login_required_admin
def zone_cordinator():
    return render_template('zone_cord.html')



#RENDERING AREA AND ZONES COORDINATOR ADD PAGE
@app.route('/new_area_cord')
@login_required_admin
def new_area_cordinator():
    curs=mysql.connect.cursor()
    state="available"
    curs.execute("SELECT * FROM areas WHERE area_state=%s ORDER BY LEFT(LOWER(area_name),1)",(state,))
    area_list = curs.fetchall()
    return render_template('create_area_cord.html', area_list=area_list)


@app.route('/new_zone_cord')
@login_required_admin
def new_zone_cordinator():
    curs=mysql.connect.cursor()
    state="available"
    curs.execute("SELECT * FROM zoner WHERE zone_state=%s ORDER BY LEFT(LOWER(zone_name),1)",(state,))
    zone_list = curs.fetchall()
    return render_template('create_zone_cord.html', zone_list=zone_list)



#CREATING AREA AND ZONE COORDINATORS
@app.route('/save_coordinators',methods=['POST'])
@login_required_admin
def save_area_cord():
    curs=mysql.connect.cursor()
    cursupdate=mysql.connect.cursor()
   #NEW VALUES
    first_name=request.form['firstname']
    last_name=request.form['lastname']
    phone_number=request.form['phonenumber']
    gender=request.form['gender']
    assigned=request.form['assign_location']
    role=request.form['role']
    state=request.form['state']


    query=("INSERT INTO coordinatorz VALUES(%s, %s, %s,%s,%s,%s,%s)")
    values= (0,first_name,last_name,gender,phone_number,assigned,role)
    curs.execute(query, values)
    curs.close()

    if role=="area cordinator":
        #UPDATE THE STATUS OF THE ASSIGNED AREA
        query=("UPDATE areas SET area_state=%s WHERE area_name=%s")
        values= (state,assigned)
        cursupdate.execute(query, values)
        cursupdate.close()

    if role=="zone cordinator":
        #UPDATE THE STATUS OF THE ASSIGNED ZOne
        query=("UPDATE zoner SET zone_state=%s WHERE zone_name=%s")
        values= (state,assigned)
        cursupdate.execute(query, values)
        cursupdate.close()
    return 'area cord added'



#EDITING NUMBER OF TARGETS
@app.route('/set_target',methods=['POST'])
@login_required_admin
def set_target():
    cursupdate=mysql.connect.cursor()
   #NEW VALUES
    area_name=request.form['area_name']
    target=request.form['target_value']
    query=("UPDATE areas SET target=%s WHERE area_name=%s")
    values= (target,area_name)
    cursupdate.execute(query, values)
    cursupdate.close()
    return 'area cord added'





@app.route('/select_zone')
@login_required_regi
def select_zone():
    curs=mysql.connect.cursor()
    curs.execute("SELECT * FROM zoner ORDER BY LEFT(LOWER(zone_name),1)")
    zone_list = curs.fetchall()
    curs.close()
    return render_template('select_zone.html', zone_list=zone_list)

@app.route('/reports')
@login_required_admin
def reports():
    curszone=mysql.connect.cursor()
    curszone.execute("SELECT * FROM zoner ORDER BY LEFT(LOWER(zone_name),1)")
    zone_list = curszone.fetchall()
    curszone.close()
    return render_template('reports.html',zone_list=zone_list)

@app.route('/fielder/<int:coord_id>', methods=['GET','POST'])
@login_required_admin
def fielder(coord_id):
    curs=mysql.connect.cursor()
    query=("SELECT * FROM coordinatorz WHERE cord_id = %s")
    values= (coord_id,)
    curs.execute(query, values)
    coord_data = curs.fetchone()
    location=coord_data[5]
    total_reg=0

    if coord_data:
        query=("SELECT * FROM members WHERE residence = %s")
        values= (location,)
        total_reg=curs.rowcount
        curs.execute(query, values)

    curs.close()
    return render_template('fielder.html', coord_data=coord_data,total_reg=total_reg)



#CODE FOR REGISTRY PAGE
@app.route('/registry')
@login_required_regi
def registry():
    return render_template('registry.html')



#ADDING AND EDITING MEMBERS
@app.route('/save_member',methods=['POST'])
@login_required_regi
def save_member():
    curs=mysql.connect.cursor()
   #NEW VALUES
    first_name=request.form['firstname']
    last_name=request.form['lastname']
    phone_number=request.form['phonenumber']
    gender=request.form['gender']
    year_of_birth=request.form['year']
    zone=request.form['zone']
    residence=request.form['residence']
    admini='khama'
    save_time=datetime.now()

    query=("INSERT INTO members VALUES(%s, %s, %s,%s,%s,%s,%s,%s,%s,%s)")
    values= (0,first_name,last_name,year_of_birth,gender,residence,zone,phone_number,admini,save_time)
    curs.execute(query, values)
    curs.close()
    return 'member added'


@app.route('/edit_register/<int:member_id>', methods=['GET','POST'])
@login_required_regi
def edit_register(member_id):
    curs=mysql.connect.cursor()
    curszone=mysql.connect.cursor()
    cursarea=mysql.connect.cursor()
    query=("SELECT * FROM members WHERE member_id = %s")
    values= (member_id,)
    curs.execute(query, values)
    member_data = curs.fetchone()
    curs.close()

    curszone.execute("SELECT * FROM zoner ORDER BY LEFT(LOWER(zone_name),1)")
    zone_list = curszone.fetchall()
    curszone.close()

    cursarea.execute("SELECT * FROM areas ORDER BY LEFT(LOWER(area_name),1)")
    area_list = cursarea.fetchall()
    cursarea.close()
    return render_template('edit_member.html', member_data=member_data,zone_list=zone_list,area_list=area_list)


@app.route('/edit_member',methods=['POST'])
@login_required_regi
def edit_member():
    curs=mysql.connect.cursor()
   #NEW VALUES
    first_name=request.form['firstname']
    last_name=request.form['lastname']
    member_ID=request.form['memberID']
    phone_number=request.form['phonenumber']
    gender=request.form['gender']
    year_of_birth=request.form['year']
    zone=request.form['zone']
    residence=request.form['residence']
    admini='khama'
    edit_time = datetime.now()

    query=("UPDATE members SET firstname=%s, lastname=%s, age=%s, gender=%s, residence=%s, zone=%s, phone_number=%s, admin_id=%s,date_time=%s WHERE member_id=%s")
    values= (first_name,last_name,year_of_birth,gender,residence,zone,phone_number,admini,member_ID,edit_time)
    curs.execute(query, values)
    curs.close()
    return 'member edited'


#VIEWING REGISTRY
@app.route('/get_reg_members',methods=['POST'])
@login_required_regi
def get_reg_members():
    area_name=request.json.get('area')
    curs=mysql.connect.cursor()
    members=[]
    if area_name=="all":
        curs.execute("SELECT member_id,firstname,lastname,age,gender,residence,phone_number,zone FROM members")
        rows=curs.fetchall()
        members=[{"id": row[0], "firstname":row[1],"lastname":row[2],"age":row[3],
                "gender":row[4],"residence":row[5],"phone":row[6],"zone":row[7]} for row in rows]
        curs.close()
    else:
        curs.execute("SELECT member_id,firstname,lastname,age,gender,residence,phone_number,zone FROM members WHERE residence=%s",(area_name,))
        rows=curs.fetchall()
        members=[{"id": row[0], "firstname":row[1],"lastname":row[2],"age":row[3],
                "gender":row[4],"residence":row[5],"phone":row[6],"zone":row[7]} for row in rows]
        curs.close()
    return jsonify(members)



#GETTING ZONES AND AREAS FOR SELECT OPTIONS FOR JAVASCRIPT
@app.route('/get_zones',methods=['GET'])
def get_zones():
    curs=mysql.connect.cursor()
    curs.execute("SELECT zone_name FROM zoner")
    zones=[row[0] for row in curs.fetchall()]
    curs.close()
    return jsonify(zones)


@app.route('/get_basic_areas',methods=['GET'])
def get_basic_areas():
    curs=mysql.connect.cursor()
    curs.execute("SELECT area_name FROM areas")
    areas=[row[0] for row in curs.fetchall()]
    curs.close()
    return jsonify(areas)

@app.route('/get_areas',methods=['POST'])
def get_areas():
    zone_name=request.json.get('zone')
    curs=mysql.connect.cursor()
    curs.execute("SELECT zone_id FROM zoner WHERE zone_name=%s",(zone_name,))
    zone_id=curs.fetchone()

    if zone_id:
        curs.execute("SELECT area_name FROM areas WHERE zone_id=%s",(zone_id,))
        areas=[row[0] for row in curs.fetchall()]
        curs.close()
    else:
        areas=[]
    return jsonify(areas)



#GETTING AREA AND ZONE COORDINATORS
@app.route('/get_area_cord',methods=['POST'])
@login_required_admin
def get_area_cord():
    area_name=request.json.get('area')
    curs=mysql.connect.cursor()
    area_cords=[]
    role="area cordinator"
    if area_name=="all":
        curs.execute("SELECT cord_id,first_name,last_name,gender,phone_number,location_name FROM coordinatorz WHERE role=%s",(role,))
        rows=curs.fetchall()
        area_cords=[{"id": row[0], "firstname":row[1],"lastname":row[2],
                "gender":row[3],"phone":row[4],"location":row[5]} for row in rows]
        curs.close()
    else:
        curs.execute("SELECT cord_id,first_name,last_name,gender,phone_number,location_name FROM coordinatorz WHERE location_name=%s AND role=%s",(area_name,role,))
        rows=curs.fetchall()
        area_cords=[{"id": row[0], "firstname":row[1],"lastname":row[2],
                "gender":row[3],"phone":row[4],"location":row[5]} for row in rows]
        curs.close()

    return jsonify(area_cords)


@app.route('/get_zone_cord',methods=['POST'])
@login_required_admin
def get_zone_cord():
    zone_name=request.json.get('zone')
    curs=mysql.connect.cursor()
    role="zone cordinator"
    zone_cords=[]
    if zone_name=="all":
        curs.execute("SELECT cord_id,first_name,last_name,gender,phone_number,location_name FROM coordinatorz WHERE role=%s",(role,))
        rows=curs.fetchall()
        zone_cords=[{"id": row[0], "firstname":row[1],"lastname":row[2],
                "gender":row[3],"phone":row[4],"location":row[5]} for row in rows]
        curs.close()
    else:
        curs.execute("SELECT cord_id,first_name,last_name,gender,phone_number,location_name FROM coordinatorz WHERE location_name=%s AND role=%s",(zone_name,role))
        rows=curs.fetchall()
        zone_cords=[{"id": row[0], "firstname":row[1],"lastname":row[2],
                "gender":row[3],"phone":row[4],"location":row[5]} for row in rows]
        curs.close()
    return jsonify(zone_cords)




##GETTIN STATISTICS
@app.route('/get_statistics',methods=['POST'])
@login_required_admin
def get_statistics():
    zone_name=request.json.get('zone')
    area_name=request.json.get('area')
    identifier=request.json.get('identifier')

    male_count=0
    female_count=0
    age_group_a=0
    age_group_b=0
    age_group_c=0
    members_count=0


    if identifier=="all":
        male_count=get_gender_stats("all","","male")
        female_count=get_gender_stats("all","","female")
        age_group_a=get_age_count("all","",18,36)
        age_group_b=get_age_count("all","",37,55)
        age_group_c=get_age_count("all","",56,200)
        members_count=get_members_count("all","")
        target_count=get_target_count("all","")
        growth_rate,new_members,old_members=get_growth_rates("24h")

    if identifier=="zone":
        male_count=get_gender_stats("zone",zone_name,"male")
        female_count=get_gender_stats("zone",zone_name,"female")
        age_group_a=get_age_count("zone",zone_name,18,36)
        age_group_b=get_age_count("zone",zone_name,37,55)
        age_group_c=get_age_count("zone",zone_name,56,200)
        members_count=get_members_count("zone",zone_name)
        target_count=get_target_count("zone",zone_name)
        growth_rate,new_members,old_members=get_growth_rates("24h")


    
    elif identifier=="area":
        male_count=get_gender_stats("area",area_name,"male")
        female_count=get_gender_stats("area",area_name,"female")
        age_group_a=get_age_count("area",area_name,18,36)
        age_group_b=get_age_count("area",area_name,37,55)
        age_group_c=get_age_count("area",area_name,56,200)
        members_count=get_members_count("area",area_name)
        target_count=get_target_count("area",area_name)
        growth_rate,new_members,old_members=get_growth_rates("24h")


    


    stat_data={
        'males_count':male_count, 'females_count':female_count,
        'age_a':age_group_a,'age_b':age_group_b,'age_c':age_group_c,
        'members_count':members_count,'target_count':target_count,'growth_rate':growth_rate,
        'new_members':new_members,'old_members':old_members
    }
    return jsonify(stat_data)








def get_gender_stats(identifier,target_name,gender):
    with app.app_context():
        cursor_gender=mysql.connect.cursor()
        gender_count=0
        
        if identifier=="all":
            cursor_gender.execute("SELECT COUNT(*) FROM members WHERE gender=%s",(gender,))
            gender_count=cursor_gender.fetchone()[0]

        if identifier=="zone":
            cursor_gender.execute("SELECT COUNT(*) FROM members WHERE zone=%s AND gender=%s",(target_name,gender,))
            gender_count=cursor_gender.fetchone()[0]

        elif identifier=="area":
            cursor_gender.execute("SELECT COUNT(*) FROM members WHERE residence=%s AND gender=%s",(target_name,gender,))
            gender_count=cursor_gender.fetchone()[0]
        return gender_count

def get_age_count(identifier,target_name,min_age,max_age):
     with app.app_context():
        cursor_age=mysql.connect.cursor()
        age_count=0
        new_min=2024-max_age
        new_max=2024-min_age

        if identifier=="all":
            cursor_age.execute("SELECT COUNT(*) FROM members WHERE age BETWEEN %s AND %s",(new_min,new_max,))
            age_count=cursor_age.fetchone()[0]

        if identifier=="zone":
            cursor_age.execute("SELECT COUNT(*) FROM members WHERE age BETWEEN %s AND %s AND zone=%s",(new_min,new_max,target_name,))
            age_count=cursor_age.fetchone()[0]

        if identifier=="area":
            cursor_age.execute("SELECT COUNT(*) FROM members WHERE age BETWEEN %s AND %s AND residence=%s",(new_min,new_max,target_name,))
            age_count=cursor_age.fetchone()[0]
        return age_count



def get_members_count(identifier,target_id):
    with app.app_context():
        cursor_members=mysql.connect.cursor()
        member_count=0

        if identifier=="all":
            cursor_members.execute("SELECT COUNT(*) FROM members")
            member_count=cursor_members.fetchone()[0]

        if identifier=="zone":
            cursor_members.execute("SELECT COUNT(*) FROM members WHERE zone=%s",(target_id,))
            member_count=cursor_members.fetchone()[0]

        if identifier=="area":
            cursor_members.execute("SELECT COUNT(*) FROM members WHERE residence=%s",(target_id,))
            member_count=cursor_members.fetchone()[0]
        return member_count
    



def get_target_count(identifier,target_id):
    with app.app_context():
        cursor_target=mysql.connect.cursor()
        target_count=0

        if identifier=="all":
            cursor_target.execute("SELECT SUM(target) as target_count FROM areas")
            member_count=cursor_target.fetchone()
            target_count=member_count[0]
            cursor_target.close()

        if identifier=="zone":
            #SELECT ZONE NAME
            cursor_target.execute("SELECT zone_id FROM zoner WHERE zone_name=%s",(target_id,))
            zone_search=cursor_target.fetchone()
            zone_id=zone_search[0]
            cursor_target.execute("SELECT SUM(target) as target_count FROM areas WHERE zone_id=%s",(zone_id,))
            member_count=cursor_target.fetchone()
            target_count=member_count[0]



        if identifier=="area":
            cursor_target.execute("SELECT SUM(target) as target_count FROM areas WHERE area_name=%s",(target_id,))
            member_count=cursor_target.fetchone()
            target_count=member_count[0]
        return target_count





@app.route('/get_comparisons',methods=['POST'])
@login_required_admin
def get_comparisons():
    identifier=request.json.get('identifier')
    cursor_comparisons=mysql.connect.cursor()
    if identifier=="area":
        cursor_comparisons.execute("""SELECT residence, COUNT(*) as member_count FROM
                                    members GROUP BY residence;""")
        rows = cursor_comparisons.fetchall()
        cursor_comparisons.close()
        area_name=[row[0] for row in rows]
        member_count=[row[1] for row in rows]
        data={'area_name':area_name,'member_count':member_count}
        print(data)
    if identifier=="zone":
        cursor_comparisons.execute("""SELECT zone, COUNT(*) as member_count FROM
                                    members GROUP BY zone;""")
        rows = cursor_comparisons.fetchall()
        cursor_comparisons.close()
        area_name=[row[0] for row in rows]
        member_count=[row[1] for row in rows]
        data={'area_name':area_name,'member_count':member_count}
        print(data)
    return jsonify(data)





@app.route('/get_data',methods=['POST'])
@login_required_admin
def get_time_stats():
    zone_name=request.json.get('zone_name')
    area_name=request.json.get('area_name')
    identifier=request.json.get('identifier')
    time_interval=request.json.get('time_interval')


    #RETURNING FOR THE LAST 24 HOURS
    cursor_time=mysql.connect.cursor()
    


    if identifier=="all":
        if time_interval=="24h":
            #RETURNING FOR THE LAST 24 HOURS
    # Query to fetch registration data for the last 24 hours
            cursor_time.execute("""
                SELECT DATE_FORMAT(date_time, '%H') AS hour, COUNT(*) AS member_count
                FROM members
                WHERE date_time >= NOW() - INTERVAL 24 HOUR
                GROUP BY hour
                ORDER BY hour
            """)
            
            registration_data = cursor_time.fetchall()
            cursor_time.close()
            cursor_time.close()
            
            # Generate a list of hours for the last 24 hours
            end_time = datetime.now().replace(minute=0, second=0, microsecond=0)
            start_time = end_time - timedelta(hours=23)  # Including the current hour makes it 24 hours
            hours_range = [start_time + timedelta(hours=i) for i in range(24)]
            
            # Create a dictionary with counts for each hour
            data = {row[0]: row[1] for row in registration_data}
            
            # Calculate cumulative totals
            cumulative_total = 0
            cumulative_counts = []
            for hour in hours_range:
                hour_str = hour.strftime('%H')
                cumulative_total += data.get(hour_str, 0)
                cumulative_counts.append((hour_str, cumulative_total))
            
            # Prepare data for Chart.js
            hours = [entry[0] for entry in cumulative_counts]
            counts = [entry[1] for entry in cumulative_counts]
            
            chart_data = {
                'hours': hours,
                'counts': counts
            }
            

        if time_interval=="7d":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%Y-%m-%d') AS day, COUNT(*)
                    AS member_count FROM members WHERE date_time>= NOW()-INTERVAL 7 DAY GROUP By day ORDER BY day""")
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(days=7)
            days_range=[start_time + timedelta(days=i) for i in range(8)]
            data={row[0]:row[1] for row in member_count}

            cumulative_total = 0
            cumulative_counts = []
            for day in days_range:
                day_str = day.strftime('%Y-%m-%d')
                cumulative_total += data.get(day_str, 0)
                # Convert date to short day name
                short_day_name = day.strftime('%a')
                cumulative_counts.append((short_day_name, cumulative_total))
            
            # Prepare data for Chart.js
            days = [entry[0] for entry in cumulative_counts]
            counts = [entry[1] for entry in cumulative_counts]
            
            chart_data = {
                'hours': days,
                'counts': counts
            }


        if time_interval=="1m":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%d') AS day, COUNT(*)
                    AS member_count FROM members WHERE date_time>= NOW()-INTERVAL 1 MONTH GROUP By day ORDER BY day""")
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(days=30)

            
            days_range=[start_time + timedelta(days=i) for i in range(31)]
            days_range=[day.strftime('%d') for day in days_range]
            data={row[0]:row[1] for row in member_count}

            cumulative_total = 0
            cumulative_counts = []
            for day in days_range:
                cumulative_total += data.get(day, 0)
                cumulative_counts.append((day, cumulative_total))
            
            # Prepare data for Chart.js
            days = [entry[0] for entry in cumulative_counts]
            counts = [entry[1] for entry in cumulative_counts]
            
            chart_data = {
                'hours': days,
                'counts': counts
            }

        if time_interval=="3m":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%m') AS day, COUNT(*)
                    AS member_count FROM members WHERE date_time>= NOW()-INTERVAL 3 MONTH GROUP By day ORDER BY day""")
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(weeks=12)

            
            days_range=[start_time + timedelta(weeks=i) for i in range(13)]
            days_range=[day.strftime('%m') for day in days_range]
            data={row[0]:row[1] for row in member_count}

            cumulative_total = 0
            cumulative_counts = []
            for day in days_range:
                cumulative_total += data.get(day, 0)
                cumulative_counts.append((day, cumulative_total))
            
            # Prepare data for Chart.js
            days = [entry[0] for entry in cumulative_counts]
            counts = [entry[1] for entry in cumulative_counts]
            
            chart_data = {
                'hours': days,
                'counts': counts
            }




    if identifier=="area":
        if time_interval=="24h":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%%H') AS hour, COUNT(*)
                    AS member_count FROM members WHERE residence=%s AND date_time>= NOW()-INTERVAL 24 HOUR GROUP By hour ORDER BY hour""",(area_name,))
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(hours=24)

            
            hours_range=[start_time + timedelta(hours=i) for i in range(25)]
            hours_range=[hour.strftime('%H') for hour in hours_range]
            data = {row[0]: row[1] for row in member_count}
            
            # Calculate cumulative totals
            cumulative_total = 0
            cumulative_counts = []
            for hour in hours_range:
                cumulative_total += data.get(hour, 0)
                cumulative_counts.append((hour, cumulative_total))
            
            # Prepare data for Chart.js
            hours = [entry[0] for entry in cumulative_counts]
            counts = [entry[1] for entry in cumulative_counts]
            
            chart_data = {
                'hours': hours,
                'counts': counts
            }


        if time_interval=="7d":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%%d') AS day, COUNT(*)
                    AS member_count FROM members WHERE residence=%s AND date_time>= NOW()-INTERVAL 7 DAY GROUP By day ORDER BY day""",(area_name,))
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(days=7)

            
            days_range=[start_time + timedelta(days=i) for i in range(8)]
            days_range=[day.strftime('%d') for day in days_range]
            data={row[0]:row[1] for row in member_count}

            cumulative_total = 0
            cumulative_counts = []
            for day in days_range:
                cumulative_total += data.get(day, 0)
                cumulative_counts.append((day, cumulative_total))
            
            # Prepare data for Chart.js
            days = [entry[0] for entry in cumulative_counts]
            counts = [entry[1] for entry in cumulative_counts]
            
            chart_data = {
                'hours': days,
                'counts': counts
            }



        if time_interval=="1m":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%%d') AS day, COUNT(*)
                    AS member_count FROM members WHERE residence=%s AND date_time>= NOW()-INTERVAL 1 MONTH GROUP By day ORDER BY day""",(area_name,))
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(days=30)

            
            days_range=[start_time + timedelta(days=i) for i in range(31)]
            days_range=[day.strftime('%d') for day in days_range]
            data={row[0]:row[1] for row in member_count}
            
            cumulative_total = 0
            cumulative_counts = []
            for day in days_range:
                cumulative_total += data.get(day, 0)
                cumulative_counts.append((day, cumulative_total))
            
            # Prepare data for Chart.js
            days = [entry[0] for entry in cumulative_counts]
            counts = [entry[1] for entry in cumulative_counts]
            
            chart_data = {
                'hours': days,
                'counts': counts
            }


            
        if time_interval=="3m":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%%m') AS day, COUNT(*)
                    AS member_count FROM members WHERE residence=%s AND date_time>= NOW()-INTERVAL 3 MONTH GROUP By day ORDER BY day""",(area_name,))
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(weeks=12)

            
            days_range=[start_time + timedelta(weeks=i) for i in range(13)]
            days_range=[day.strftime('%m') for day in days_range]
            data={row[0]:row[1] for row in member_count}

            complete_data={day:data.get(day,0) for day in days_range}
            cursor_time.close()
            
            #PREPARE DATA TO RETURN
            chart_data={'hours':days_range,'counts':[complete_data[day] for day in days_range]}





    if identifier=="zone":
        if time_interval=="24h":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%%H') AS hour, COUNT(*)
                    AS member_count FROM members WHERE date_time>= NOW()-INTERVAL 24 HOUR AND zone=%s GROUP By hour ORDER BY hour""",(zone_name,))
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(hours=24)

            
            hours_range=[start_time + timedelta(hours=i) for i in range(25)]
            hours_range=[hour.strftime('%H') for hour in hours_range]
            data={row[0]:row[1] for row in member_count}

            complete_data={hour:data.get(hour,0) for hour in hours_range}
            cursor_time.close()
            
            #PREPARE DATA TO RETURN
            chart_data={'hours':hours_range,'counts':[complete_data[hour] for hour in hours_range]}


        if time_interval=="7d":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%%d') AS day, COUNT(*)
                    AS member_count FROM members WHERE zone=%s AND date_time>= NOW()-INTERVAL 7 DAY GROUP By day ORDER BY day""",(zone_name,))
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(days=7)

            
            days_range=[start_time + timedelta(days=i) for i in range(8)]
            days_range=[day.strftime('%d') for day in days_range]
            data={row[0]:row[1] for row in member_count}

            complete_data={day:data.get(day,0) for day in days_range}
            cursor_time.close()
            
            #PREPARE DATA TO RETURN
            chart_data={'hours':days_range,'counts':[complete_data[day] for day in days_range]}


        if time_interval=="1m":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%%d') AS day, COUNT(*)
                    AS member_count FROM members WHERE zone=%s AND date_time>= NOW()-INTERVAL 1 MONTH GROUP By day ORDER BY day""",(zone_name,))
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(days=30)

            
            days_range=[start_time + timedelta(days=i) for i in range(31)]
            days_range=[day.strftime('%d') for day in days_range]
            data={row[0]:row[1] for row in member_count}

            complete_data={day:data.get(day,0) for day in days_range}
            cursor_time.close()
            
            #PREPARE DATA TO RETURN
            chart_data={'hours':days_range,'counts':[complete_data[day] for day in days_range]}


        if time_interval=="3m":
            #RETURNING FOR THE LAST 24 HOURS
            cursor_time.execute("""SELECT DATE_FORMAT(date_time, '%%m') AS day, COUNT(*)
                    AS member_count FROM members WHERE zone=%s AND date_time>= NOW()-INTERVAL 3 MONTH GROUP By day ORDER BY day""",(zone_name,))
            member_count=cursor_time.fetchall()
            end_time=datetime.now()
            start_time=end_time-timedelta(weeks=12)

            
            days_range=[start_time + timedelta(weeks=i) for i in range(13)]
            days_range=[day.strftime('%m') for day in days_range]
            data={row[0]:row[1] for row in member_count}

            complete_data={day:data.get(day,0) for day in days_range}
            cursor_time.close()
            
            #PREPARE DATA TO RETURN
            chart_data={'hours':days_range,'counts':[complete_data[day] for day in days_range]}

    return jsonify(chart_data)



#GENERATE REPORTS
@app.route('/generate_report', methods=['GET'])
def generate_report():
    zone_name=request.args.get('zone_name')
    time_range=request.args.get('time_range')
    curs=mysql.connect.cursor()
    role="zone cordinator"
    
    #GET DATE
    current_date=datetime.now()

    #ZONE CORDINATOR NAME ADN NUMBER
    curs.execute("SELECT first_name,last_name,phone_number FROM coordinatorz WHERE location_name=%s AND role=%s",(zone_name,role))
    rows=curs.fetchone()
    zone_cord_firstname=rows[0]
    zone_cord_lastname=rows[1]
    zone_cord_phone_number=rows[2]
    curs.close()


    #GET NEW MEMBERS


    #GET TOTAL MEMBERS
    members_count=get_members_count("zone",zone_name)

    #GET TARGET
    target_count=get_target_count("zone",zone_name)

    #GET GENDER COUNT
    male_count=get_gender_stats("zone",zone_name,"male")
    female_count=get_gender_stats("zone",zone_name,"female")


    #GET AGE STATS
    age_group_a=get_age_count("zone",zone_name,18,36)
    age_group_b=get_age_count("zone",zone_name,37,55)
    age_group_c=get_age_count("zone",zone_name,56,200)


       


    
  
    generate_pdf(current_date,zone_name, time_range,members_count,target_count,male_count,female_count,age_group_a,age_group_b,age_group_c, zone_cord_firstname,zone_cord_lastname,zone_cord_phone_number)

    return send_file(f"{zone_name}.pdf", as_attachment=True)


def generate_pdf(current_date,zone_name, time_range,members_count,target_count,male_count,female_count,age_group_a,age_group_b,age_group_c, zone_cord_firstname,zone_cord_lastname,zone_cord_phone_number):
    with app.app_context():
        curs=mysql.connect.cursor()
        curs.execute("SELECT zone_id FROM zoner WHERE zone_name=%s",(zone_name,))
        rows=curs.fetchone()
        zone_id=rows[0]

        curs.execute("SELECT area_name FROM areas WHERE zone_id=%s",(zone_id,))
        rows_areas=curs.fetchall()

        time_name=""
        if time_range=="24h":
            time_name="24hours"
        if time_name=="7d":
            time_name="7days"
        if time_name=="30d":
            time_name="1month"
        if time_name=="3m":
            time_name="3months"

    # Create PDF
        progress=(members_count/target_count)*100
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)
        pdf.cell(0,10,f"Reports for the last {time_name}",0,1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0,10,f"{zone_name}",0,1)
        pdf.cell(0,10,f"Date: {current_date}",0,1)
        pdf.cell(0,10,f"Zone coordinator: {zone_cord_firstname} {zone_cord_lastname}",0,1)
        pdf.cell(0,10,f"Phone number: {zone_cord_phone_number}",0,1)
        pdf.cell(0,5,"",0,1)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0,10,"General statistics",0,1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0,10,"New members: 1200",0,1)
        pdf.cell(0,10,f"Total members: {members_count}",0,1)
        pdf.cell(0,10,f"Target: {target_count}",0,1)
        pdf.cell(0,10,f"Progress: {progress}%",0,1)
        pdf.cell(0,10,"Growth rate: 15%",0,1)
        pdf.cell(0,5,"",0,1)

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0,10,"Gender and Age Distribution",0,1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0,10,f"Gender distribution: {male_count} Females: {female_count}",0,1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0,10,f"Age distribution: 18-35: {age_group_a}, 36-55years: {age_group_b}, 56+: {age_group_c}",0,1)
        pdf.cell(0,5,'',0,1)

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0,10,"Member count in Areas",0,1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(40,8,'Area name',1,0, 'C')
        pdf.cell(30,8,'Target members',1,0, 'C')
        pdf.cell(30,8,'Total members',1,0, 'C')
        pdf.cell(60,8,'Coordinator',1,0, 'C')
        pdf.cell(30,8,'Phone number',1,1, 'C')

       

        for rows in rows_areas:
            area_name=rows[0]
            role="area cordinator"
            curs.execute("SELECT first_name,last_name,phone_number FROM coordinatorz WHERE location_name=%s AND role=%s",(area_name,role))
            rows_cord=curs.fetchone()
            if rows_cord:
                area_cord_firstname=rows_cord[0]
                area_cord_lastname=rows_cord[1]
                area_cord_phone_number=rows_cord[2]
            else:
                area_cord_firstname="N/A"
                area_cord_lastname="N/A"
                area_cord_phone_number="N/A"


            members_count=get_members_count("area",area_name)

            target_count=get_target_count("area",area_name)


            pdf.cell(40,8,f"{area_name}",1,0, 'R')
            pdf.cell(30,8,f"{target_count}",1,0, 'R')
            pdf.cell(30,8,f"{members_count}",1,0, 'R')
            pdf.cell(60,8,f"{area_cord_firstname} {area_cord_lastname}",1,0, 'R')
            pdf.cell(30,8,f"{area_cord_phone_number}",1,1, 'R')


        pdf.cell(0,10,"",0,1)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0,10,"NEXT PAGE: List of all registered members",0,1)
        
        # Save the PDF
        pdf.output(f"{zone_name}.pdf")




#GET LIST OF MEMBERS PER ZONE FOR THE REPORT
def get_members_by_areas(zone_name,time_interval):
    with app.app_context():
        cursor = mysql.connect.cursor()
        members_by_area = {}
        interval=""


        if time_interval=="24h":
            interval=datetime.now()-timedelta(hours=24)
        if time_interval=="7d":
            interval=datetime.now()-timedelta(days=7)
        if time_interval=="30d":
            interval=datetime.now()-timedelta(days=30)
        if time_interval=="3m":
            interval=datetime.now()-timedelta(days=90)
        
        cursor.execute("""
            SELECT residence, firstname, lastname, age, gender, date_time
            FROM members
            WHERE zone = %s AND date_time >= %s
            ORDER BY residence ASC, lastname, firstname
        """, (zone_name, interval))
        
        members = cursor.fetchall()
        cursor.close()
        
        # Group members by area
        for member in members:
            area, firstname, lastname,age, gender, date_time = member
            if area not in members_by_area:
                members_by_area[area] = []
            members_by_area[area].append({
                'first_name': firstname,
                'last_name': lastname,
                'age': age,
                'gender': gender,
                'date_time': date_time,
                'residence': area
            })
    return members_by_area




def get_growth_rates(time_interval):
    with app.app_context():
        cursor_new=mysql.connect.cursor()
        cursor_old=mysql.connect.cursor()
        interval=""
        
        if time_interval=="24h":
            interval=datetime.now()-timedelta(hours=24)
            interval_two=datetime.now()-timedelta(hours=48)
        if time_interval=="7d":
            interval=datetime.now()-timedelta(days=7)
            interval_two=datetime.now()-timedelta(days=14)
        if time_interval=="30d":
            interval=datetime.now()-timedelta(days=30)
            interval_two=datetime.now()-timedelta(days=60)
        if time_interval=="3m":
            interval=datetime.now()-timedelta(days=90)
            interval_two=datetime.now()-timedelta(days=180)

        cursor_new.execute('SELECT COUNT(*) AS new_members FROM members WHERE date_time>=%s',(interval,))
        new_members = cursor_new.fetchone()[0]
        cursor_old.execute('SELECT COUNT(*) AS new_members FROM members WHERE date_time>=%s AND date_time< %s',(interval_two,interval,))
        old_members = cursor_old.fetchone()[0]

        if old_members:
            if new_members>0:
                growth_rate=((new_members-old_members) /old_members) *100
                rate=f'{round(growth_rate)}'
            else:
                growth_rate=float('inf')

        else:
            growth_rate=float('inf')
        cursor_new.close()
        cursor_old.close()
        return growth_rate, new_members,old_members




if __name__== '__main__':
   app.run( host='0.0.0.0',port=5000,debug=True,use_reloader=False)