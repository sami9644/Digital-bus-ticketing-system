from flask import *
import database as db
from functools import wraps
import os

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
    return render_template('dashboard.html',userinfo=db.userinfo(session['userid']),tickets=db.tickets())

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

@app.route("/recharge")
@login_required
def recharge():
    return render_template("recharge.html")

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




@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')



