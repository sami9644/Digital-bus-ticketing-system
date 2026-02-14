from flask import *
import pymysql
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime
import os

def connection():
	conn = pymysql.connect(user='root',password='Sami@49987315',database='busdb',host='127.0.0.1')
	return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user info exists in session
        if 'loggedin' not in session:
            # flash("You must be logged in to access this page.", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = "fgiodshgioerggioh"

@app.errorhandler(404)
def page_not_found(e):
    # Note: We set the 404 status explicitly
    return render_template('404page.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    # Note: We set the 500 status explicitly
    return render_template('500.html'), 500

@app.route("/")
def admin_login():
	if not session.get("loggedin"):
		return render_template("index.html")
	return redirect(url_for('admin_dash'))

@app.route("/login",methods=['POST'])
def login():
	username = request.form.get('username')
	password = request.form.get('password')
	with connection() as conn:
		cur = conn.cursor()
		cur.execute("SELECT * FROM admins WHERE username = %s AND password_ = %s",(username,password))
		data = cur.fetchone()
	if data:
		session['loggedin'] = True
		return redirect(url_for('admin_dash'))
	else:
		return "<script>alert('invalid credentials!')</script>"

@app.route("/admin/dash")
@login_required
def admin_dash():
	return render_template("dashboard.html")

@app.route("/register/bus",methods=['GET','POST'])
@login_required
def registerBus():
	if request.method == 'GET':
		return render_template("register.html")
	elif request.method == 'POST':
		plateno = request.form.get("plateno")
		telno = request.form.get("telno")
		fullname = request.form.get("fullname")
		photo = request.files.get("photo")
		filepath = f'static/{plateno}.jpg'
		photo.save(filepath)
		with connection() as conn:
			cur = conn.cursor()
			cur.execute("INSERT INTO buses VALUES(%s,%s,%s,%s)",(plateno,fullname,telno,filepath))
			conn.commit()
		return 'Successfully registered!<a href="/">Go home </a>'
	else:
		return request.method+" isnt allowed",405

@app.route("/manage/bus")
@login_required
def managebus():
	with connection() as conn:
			cur = conn.cursor()
			cur.execute("SELECT * FROM buses")
			data = cur.fetchall()
	return render_template("manage.html",buses= data)

@app.route("/edit/bus/<id>")
@login_required
def editbus(id):
    with connection() as conn:
        cur = conn.cursor()
        # Fetch the specific bus details
        cur.execute("SELECT * FROM buses WHERE plate_no = %s", (id,))
        bus_data = cur.fetchone() 
    return render_template("edit.html", bus=bus_data)

@app.route("/update/bus/<string:plate_no>", methods=['POST'])
@login_required
def update_bus(plate_no):
    # 1. Get form data
    fullname = request.form.get('fullname')
    telno = request.form.get('telno')
    file = request.files.get('photo')

    with connection() as conn:
        cur = conn.cursor()

        # 2. Handle the Image Logic
        if file and file.filename != '':
            # User uploaded a new photo
            filename = secure_filename(f"{plate_no}")
            file.save(os.path.join('static/', filename))
            
            # Update everything including the photo path
            cur.execute("""
                UPDATE buses 
                SET driver_name = %s, driver_phone_no = %s, driver_photo = %s 
                WHERE plate_no = %s
            """, (fullname, telno, os.path.join('static/', filename), plate_no))
        else:
            # No new photo uploaded, update only text fields
            cur.execute("""
                UPDATE buses 
                SET driver_name = %s, driver_phone_no = %s 
                WHERE plate_no = %s
            """, (fullname, telno, plate_no))
        
        conn.commit()
    
    flash(f"Bus {plate_no} updated successfully!", "success")
    return redirect(url_for('managebus'))

@app.route("/delete/bus/<string:plate_no>")
@login_required
def delete_bus(plate_no):
    with connection() as conn:
        cur = conn.cursor()
        
        # Optional: Get the photo filename first to delete the file from the server
        cur.execute("SELECT driver_photo FROM buses WHERE plate_no = %s", (plate_no,))
        result = cur.fetchone()
        
        if result:
            photo_filename = result[0]
            # Delete the record from the database
            cur.execute("DELETE FROM tickets WHERE bus = %s", (plate_no,))
            cur.execute("DELETE FROM buses WHERE plate_no = %s", (plate_no,))
            conn.commit()
            
            # Delete the physical file from the static folder to save space
            try:
                if photo_filename:
                    file_path = os.path.join('static/', photo_filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")

    flash(f"Bus {plate_no} and associated driver data removed.", "info")
    return redirect(url_for('managebus'))


@app.route("/generate/ticket", methods=['GET', 'POST'])
@login_required
def generate_ticket():
    with connection() as conn:
        cur = conn.cursor()
        
        if request.method == 'POST':
            # 1. Process the Form Submission
            price = request.form.get('price')
            bus_plate = request.form.get('bus')
            address = request.form.get('address')
            
            # Generate Ticket ID using current timestamp (YYYYMMDDHHMMSS)
            ticket_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            addedon = datetime.now().strftime("%Y-%m-%d")
            
            try:
                cur.execute("""
                    INSERT INTO tickets (ticketid, price, bus, address,addedon) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (ticket_id, price, bus_plate, address,addedon,))
                conn.commit()
                flash(f"Ticket {ticket_id} generated successfully!", "success")
                return redirect(url_for('managetickets')) # Assuming you have this route
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
                return redirect(url_for('generate_ticket'))

        # 2. Handle GET Request: Fetch buses for the dropdown
        cur.execute("SELECT plate_no, driver_name FROM buses")
        buses = cur.fetchall()
        
    return render_template("generate_ticket.html", buses=buses)


@app.route("/manage/tickets")
@login_required
def managetickets():
    with connection() as conn:
        cur = conn.cursor()
        # Using a JOIN to get the driver's name from the buses table
        query = """
            SELECT t.ticketid, t.price, t.bus, t.address, b.driver_name 
            FROM tickets t
            JOIN buses b ON t.bus = b.plate_no
            ORDER BY t.ticketid DESC
        """
        cur.execute(query)
        tickets_data = cur.fetchall()
    return render_template("manage_tickets.html", tickets=tickets_data)

@app.route("/delete/ticket/<string:ticketid>")
@login_required
def delete_ticket(ticketid):
    with connection() as conn:
        cur = conn.cursor()
        
        # Check if ticket exists before attempting delete
        cur.execute("DELETE FROM tickets WHERE ticketid = %s", (ticketid,))
        conn.commit()
        
    flash(f"Ticket {ticketid} has been voided/deleted.", "warning")
    return redirect(url_for('managetickets'))

@app.route("/logout")
def logout():
	session.clear()
	return redirect(url_for('admin_login'))


if __name__ == '__main__':
	app.run(debug=True,port ='3000')