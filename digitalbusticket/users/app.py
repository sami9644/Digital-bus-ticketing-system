from flask import *
import database as db
from functools import wraps
import os
import time
from chapa_utils import initialize_payment,verify_payment

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user info exists in session
        if 'userid' not in session:
            # flash("You must be logged in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = 'HJDUhsuidhwiefhiwehUyywegf8uwgefuie'

@app.before_request
def make_perm():
    session.permanent = True


@app.route('/')
def home():
    return redirect(url_for('signup'))

@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        phone = request.form.get("phone")
        # pic = request.files.get('pic')
        birthdate = request.form.get("birthdate")
        password_ = request.form.get('password_')
        picture = 'static/profilepicture/dp.jfif'
        reg = db.register_user(fullname,phone,picture,birthdate,password_)
        if reg == 'duplicate':
            return render_template('response.html',responsetext='Phone number already used!',resurl='/signup')
        elif reg == 'unknown error':
            return render_template('response.html',responsetext='Unknown error occured try again!',resurl='/signup')
        elif reg == 'not eligible':
            return render_template('response.html',responsetext='You need to be atleast 18',resurl='/signup')
        return render_template('response.html',responsetext='Your account has been successfully registered!',resurl='/signup')
    return render_template('index.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get("phone")
        password_ = request.form.get('password_')
        loginu= db.login(phone,password_)
        if loginu == 'invalid':
            return render_template('response.html',responsetext='password or phone number is invalid!',resurl='/login')
        elif loginu == 'error':
            return render_template('response.html',responsetext='Unknown error occured!',resurl='/login')
        session['userid'] = loginu[0]
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',userinfo=db.userinfo(session['userid']),tickets=db.tickets(),ispaid=db.isticket_paid(session['userid']))

@app.route("/ticket/search")
@login_required
def ticket_search():
    ticketno = request.args.get("ticketno")
    ticket_data = db.ticket_data(ticketno)
    if ticket_data:
        return render_template("ticket.html",userinfo=db.userinfo(session['userid']),ticket_data=ticket_data,ispaid=db.ispaid(ticketno,session['userid']))
    else:
        return "<script>alert('ticket not found!');window.location.href='/dashboard'</script>",404

@app.route("/change/picture",methods=['GET',"POST"])
@login_required
def change_picture():
    if request.method == 'POST':
        dp = request.files.get('dp')
        filepath = os.path.join('static','profilepicture',f"{session['userid']}.jpg")
        profilepic = dp.save(filepath)
        db.uploaddp(filepath,session['userid'])
        return 'profile picture successfully changed!<br> <a href="/change/picture">Go back</a>'
    return render_template('change_dp.html',userinfo=db.userinfo(session['userid']))




@app.route("/change/password",methods=["GET","POST"])
@login_required
def change_password():
    if request.method == 'POST':
        old = request.form['old']
        new = request.form['new']
        changepas = db.change_password(old,new,session['userid'])
        if changepas == 'old':
            return 'Wrong old password<br> <a href="/change/password">Go back</a>'
        elif changepas == 'unknown error':
            return 'An error occured!<br> <a href="/change/password">Go back</a>'
        return 'Password successfully changed!<br> <a href="/change/password">Go back</a>'
    return render_template("changepas.html",userinfo=db.userinfo(session['userid']))

@app.route("/qrcode")
@login_required
def qrcode():
    return render_template("qrcode.html")


# import pymysql

@app.route('/history')
@login_required
def payment_history():
    payments = db.paymentinfo(session['userid'])
    return render_template("history.html",payments=payments,tic=db.ticket_id)


from flask import redirect, make_response, request, render_template, session

@app.route("/pay/<ticketid>", methods=['GET', 'POST'])
@login_required
def payticket(ticketid):
    if request.method == "GET":
        return render_template("paytick.html", ticketid=ticketid, price=db.ticket_id(ticketid)[1])
    
    elif request.method == "POST":
        totalpersons = request.form.get("totalpersons")
        price = db.ticket_id(ticketid)[1]
        connection = db.database_conn()
        full_host = request.host_url
        
        # 1. Generate unique ID
        tx_ref = db.generate_unique_id(connection, 'payment', 'transactionid')
        
        # 2. Get the Chapa Checkout URL
        checkout_url = initialize_payment(
            price, 
            'ethiofreelancer96@gmail.com', 
            tx_ref, 
            f'{full_host}verify/payment', 
            f'{full_host}verify/payment'
        )
        
        # 3. Create the Redirect response FIRST
        response = make_response(redirect(checkout_url))
        
        # 4. Attach cookies to that specific redirect response
        response.set_cookie('price', str(price))
        response.set_cookie("totper", str(totalpersons))
        response.set_cookie("tx_ref", str(tx_ref))
        response.set_cookie("ticket", str(ticketid))
        
        return response

@app.route("/verify/payment")
@login_required
def verifypayment():
    # Retrieve cookies
    tx_ref = request.cookies.get("tx_ref")
    
    # Safety Check: If cookies are missing, don't try to touch the DB
    if not tx_ref:
        return render_template("verify.html", message="Session expired or invalid transaction.")

    # Check Chapa status first
    ispaid = verify_payment(tx_ref)
    
    if ispaid:
        price = request.cookies.get('price')
        total_persons = request.cookies.get('totper')
        ticket = request.cookies.get("ticket")
        
        # Only insert into DB if payment is confirmed
        db.payforticket(tx_ref, price, total_persons, session['userid'], ticket)
        
        return render_template("verify.html", message="Payment successfully made!")
    
    return render_template("verify.html", message="Error occurred while making payment")
        



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')



