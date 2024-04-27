from flask import Blueprint, Flask, render_template,request,flash,redirect,session,url_for
import os
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Website/static/upload'


try:
    conn=mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        port='3306'
    )
    if conn.is_connected():
        print("connected")
except:
    print("issues with connection")
cur=conn.cursor()
cur.execute("use rentalmanagement")
# with open('schema.sql', 'r') as f:
#     cur.execute(f.read())
#     conn.commit()
auth= Blueprint('auth',__name__, static_folder='static')
@auth.route('/base')
def base():
    return render_template('base.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        address = request.form.get('address')
        phoneNumber = request.form.get('phoneNumber')
        password1 = request.form.get('password1')
        password2 = request.form.get('password')

        # Form Validation
        if len(email) < 4:
            flash('Email must have greater than 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First Name must have greater than 1 character.', category='error')
        elif len(password1) < 7:
            flash('Password must have greater than 7 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif not password1.isalnum():
            flash('Password must contain only alphanumeric characters.', category='error')
        elif not phoneNumber.isdigit():
            flash('Phone Number must contain only digits.', category='error')
        else:
            # Check if email already exists in the database
            cur.execute("SELECT * FROM Landlord WHERE LEmail = %s", (email,))
            existing_user = cur.fetchone()
            if existing_user:
                flash('Email already exists.', category='error')
            else:
                # Input Sanitization and Database Operation
                try:
                    cur.execute('''INSERT INTO Landlord
                                    (LFname, LLname, LEmail, Lphone, LAddress, LPassword)
                                    VALUES (%s, %s, %s, %s, %s, %s)''',
                                (firstName, lastName, email, phoneNumber, address, password1))
                    conn.commit()
                    cur.execute("SELECT LAST_INSERT_ID();")
                    lid = cur.fetchone()[0]
                    session['lid'] = lid
                    return redirect("/home")
                except Exception as e:
                    conn.rollback()
    return render_template('signup.html')

@auth.route('/home', methods=['GET', 'POST'])
def home():
    # Retrieve the landlord ID from the session
    lid = session.get('lid')
    if lid:
            # Fetch all properties associated with the current landlord
            cur.execute('''SELECT *
                            FROM Property
                            WHERE Lid = %s''', (lid,))
            properties = cur.fetchall()
            if properties:
                print(properties[0])
            # Pass the fetched properties to the template for rendering
                return render_template('home.html', properties=properties)
    return render_template('home.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email') 
        paswd = request.form.get('password')
        sql = '''
                SELECT Lid, LPassword
                FROM Landlord
                WHERE LEmail = %s
            '''
        try:
            cur.execute(sql, (email,))
            data = cur.fetchone()
            if data:
                lid, stored_password = data  # Fetch Lid and stored password from database
                if stored_password == paswd:
                    session['lid'] = lid  # Store Lid in session
                    return redirect('/home')
                else:
                    flash('The entered password is incorrect', category='error')                 
            else:
                flash('The email id doesn\'t exist', category='error')
        except Exception as e:
            flash(str(e), category='error')
    return render_template('login.html')

@auth.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@auth.route('/propertyform', methods=['GET', 'POST'])
def propertyform():
    if request.method == 'POST':
        lid = session.get('lid')
        if lid:
            PCategory = request.form.get('PCategory')
            PLocation = request.form.get('PLocation')
            PCity = request.form.get('PCity')
            PState = request.form.get('PState')
            PPin = request.form.get('PPin')
            # PPhoto = request.files['PPhoto']

            # if PPhoto:
            #     # Save the file to your desired directory
            #     photo_filename = secure_filename(PPhoto.filename)
            #     photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            #     PPhoto.save(photo_path)

            try:
                # Insert property details into the Property table
                cur.execute('''INSERT INTO Property
                                (Lid, PCategory, PLocation, PCity, PState, PPin)
                                VALUES (%s, %s, %s, %s, %s, %s)''',
                            (lid, PCategory, PLocation, PCity, PState, PPin))
                conn.commit()
                return redirect('/home')  # Redirect to home page after successful insertion
            except Exception as e:
                flash(str(e), category='error')
                conn.rollback()
    return render_template('propertyform.html')

@auth.route('/<int:pid>/tenantpage', methods=['GET', 'POST'])
def tenantpage(pid):
    session['pid'] = pid

    # Query the database to fetch updated tenant data based on pid
    cur.execute('''SELECT TFname, TLname, Rent, PaymentStatus, PayDate , Tenant.Tid , Lid
                    FROM Tenant
                    JOIN Rent ON Tenant.Tid = Rent.Tid
                    WHERE Pid = %s
                    ORDER BY PayDate''', (pid,))
    tenant_data = cur.fetchall()

    cur.execute('''SELECT *
                    FROM Property
                    WHERE Pid = %s''', (pid,))
    property_details = cur.fetchone()

    # Pass tenant data and property details to the template for rendering
    return render_template('tenantpage.html', tenant_data=tenant_data, property_details=property_details)
@auth.route('/sortdate', methods=['GET', 'POST'])
def sortdate():
    return redirect(url_for('auth.tenantpage', pid=session['pid']))
@auth.route('/sortname', methods=['GET', 'POST'])
def sortname():
    pid=session['pid']
    # Query the database to fetch updated tenant data based on pid
    cur.execute('''SELECT TFname, TLname, Rent, PaymentStatus, PayDate,Tenant.Tid , Lid
                    FROM Tenant
                    JOIN Rent ON Tenant.Tid = Rent.Tid
                    WHERE Pid = %s
                    ORDER BY TFName''', (pid,))
    tenant_data = cur.fetchall()

    cur.execute('''SELECT *
                    FROM Property
                    WHERE Pid = %s''', (pid,))
    property_details = cur.fetchone()

    # Pass tenant data and property details to the template for rendering
    return render_template('tenantpage.html', tenant_data=tenant_data, property_details=property_details)
@auth.route('/sortpaid', methods=['GET', 'POST'])
def sortpaid():
    pid=session['pid']
    # Query the database to fetch updated tenant data based on pid
    cur.execute('''SELECT TFname, TLname, Rent, PaymentStatus, PayDate,Tenant.Tid , Lid
                    FROM Tenant
                    JOIN Rent ON Tenant.Tid = Rent.Tid
                    WHERE Pid = %s
                    ORDER BY PaymentStatus desc''', (pid,))
    tenant_data = cur.fetchall()

    cur.execute('''SELECT *
                    FROM Property
                    WHERE Pid = %s''', (pid,))
    property_details = cur.fetchone()

    # Pass tenant data and property details to the template for rendering
    return render_template('tenantpage.html', tenant_data=tenant_data, property_details=property_details)
@auth.route('/tenantform', methods=['GET', 'POST'])
def tenantform():
    if request.method == 'POST':
        pid = session['pid']  # Assuming you have a way to get the property ID
        TFname = request.form.get('TFname')
        TLname = request.form.get('TLname')
        TEmail = request.form.get('TEmail')
        TPhone = request.form.get('TPhone')
        DOC = request.form.get('DOC')

        Deposit = request.form.get('Deposit')
        Rent = request.form.get('Rent')
        PaymentStatus = request.form.get('PaymentStatus')
        PayDate = request.form.get('PayDate')

        try:
            # Insert Tenant details into the Tenant table
            cur.execute('''INSERT INTO Tenant
                            (TFname, TLname, TEmail, TPhone, DOC, Pid)
                            VALUES (%s, %s, %s, %s, %s, %s)''',
                        (TFname, TLname, TEmail, TPhone, DOC, pid))
            conn.commit()

            # Get the Tid of the newly inserted Tenant
            cur.execute('SELECT LAST_INSERT_ID()')
            tid = cur.fetchone()[0]

            # Insert Rental details into the Rent table
            cur.execute('''INSERT INTO Rent
                            (Lid, Tid, Deposit, Rent, PaymentStatus, PayDate)
                            VALUES (%s, %s, %s, %s, %s, %s)''',
                        (session.get('lid'), tid, Deposit, Rent, PaymentStatus, PayDate))
            conn.commit()

            return redirect(url_for('auth.tenantpage', pid=session['pid'])) # Redirect to home page after successful insertion
        except Exception as e:
            conn.rollback()

    return render_template('tenantform.html')



@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    # Remove the user's session data
    session.clear()
    # Redirect the user to the login page (or any other page you prefer)
    return redirect('/base')


@auth.route('/<int:tid>/<int:lid>/deletetenant', methods=['GET', 'POST'])
def deletetenant(tid, lid):
        print(tid)
        print(lid)
        try:
            # Delete Tenant from Tenant table
            cur.execute('''DELETE FROM Tenant
                            WHERE Tid = %s''',
                        (tid,))
            conn.commit()
            print(tid)
            print(lid)

            # Delete corresponding rental information from Rent table
            cur.execute('''DELETE FROM Rent
                            WHERE Tid = %s''',
                        (lid,))
            conn.commit()
            # Redirect to tenant page after successful deletion  
        except Exception as e:
            conn.rollback()

    # If the request method is GET, render the confirmation page for tenant deletion
    # You can have a confirmation page or directly perform the deletion via JavaScript confirmation
        return redirect(url_for('auth.tenantpage', pid=session['pid'])) 
@auth.route('/<int:tid>/<int:lid>/updatetenant', methods=['GET', 'POST'])
def updatetenant(tid, lid):
    if request.method == 'POST':
        # Retrieve updated information from the form
        payment_status = request.form.get('UpdatedPaymentStatus')
        payment_date = request.form.get('UpdatedPayDate')
        payment_rent=request.form.get('UpdatedRent')
        print(payment_date,payment_rent,payment_status)
        print(tid)
        try:
            # Update Tenant table
            # Update Rent table
            cur.execute('''UPDATE Rent
                            SET PaymentStatus = %s, PayDate = %s,rent=%s
                            WHERE Tid = %s''',
                        (payment_status, payment_date, payment_rent, tid))
            conn.commit()
            print(payment_date,payment_rent,payment_status)
            # Redirect to tenant page with the updated information
            return redirect(url_for('auth.tenantpage', pid=session['pid']))  
        except Exception as e:
            conn.rollback()
    return render_template('updatetenant.html')

@auth.route('/delete', methods=['GET', 'POST'])
def delete():
    lid = session['lid']
    
    try:
        # Delete Landlord from Landlord table
        cur.execute('''DELETE FROM Landlord
                        WHERE Lid = %s''',
                    (lid,))
        conn.commit() 
    except Exception as e:
        conn.rollback()
    return redirect('/base')

@auth.route('/canceltotenantpage',methods=['GET', 'POST'])
def cancel():
    return redirect(url_for('auth.tenantpage', pid=session['pid']))
@auth.route('/profile',methods=['GET', 'POST'])
def profile():
    lid=session['lid']
    cur.execute(''' SELECT LFname,LLname,LEmail,LPhone,LAddress
                  FROM Landlord
                        WHERE Lid = %s''',
                    (lid,))
    print(lid)
    landlord_data = cur.fetchone()
    # print(landlord_data[1])
    return render_template('profile.html',landlord_data=landlord_data)