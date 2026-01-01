import pymysql
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

def check_legal_age(birth_date_str):
    """
    Accepts date in 'YYYY-MM-DD' format (standard for HTML date inputs)
    Returns True if user is exactly 18 or older today.
    """
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.now()
        
        # Calculate age accounting for the month/day
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        return age >= 18
    except ValueError:
        return "Invalid date format"

def database_conn():
    conn = pymysql.connect(host='localhost',database='busdb',password='Sami@7760365935',user='root')
    return conn

def register_user(fullname,phone,photo,birthdate,password):
    try:
        with database_conn() as conn:
            cur = conn.cursor()
            sql = 'INSERT INTO users(userid,fullname,phone_no,photo,birthdate,password_) VALUES(%s,%s,%s,%s,%s,%s)'
            hashpass = generate_password_hash(password)
            args = (str(uuid.uuid4()),fullname,phone,photo,birthdate,hashpass)
            cur.execute(sql,args)
            conn.commit()
        if not(check_legal_age(birthdate)):
            return 'not eligible'
        return 'no error'
    except pymysql.IntegrityError as e:
        print(e)
        return 'duplicate'
    except Exception as e:
        print(e)
    return 'unknown error'

def login(phone_num,password):
    try:
        with database_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE phone_no = %s",(phone_num,))
            data = cur.fetchone()
        if data and check_password_hash(data[6],password):
            return data
        return 'invalid'
    except Exception as e:
        print(e)
        return 'error'

def userinfo(userid):
    with database_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE userid = %s",(userid,))
        data = cur.fetchone()
    return data

def ticket_data(ticketno):
    with database_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE ticketid = %s",(ticketno,))
        data = cur.fetchone()
    return data

def ispaid(ticketno,paidby):
    with database_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM payment WHERE ticket = %s AND paidby = %s",(ticketno,paidby,))
        data = cur.fetchone()
    return data

def uploaddp(dp,userid):
    try:
        with database_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET photo = %s WHERE userid = %s",(dp,userid))
            conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    
def change_password(old,new,userid):
    try:
        with database_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_ FROM users WHERE userid = %s",(userid,))
            data= cursor.fetchone()
        if check_password_hash(data[0],old):
            with database_conn() as conn:
                cur= conn.cursor()
                args = (generate_password_hash(new),userid)
                cur.execute("UPDATE users SET password_ = %s WHERE userid = %s",args)
                conn.commit()
            return 'success'
        return 'old'
    except Exception as e:
        print(e)
        return "unknown error"