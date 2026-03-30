import pymysql
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
import qrcode
import os
import re
import string
import random

def database_conn():
    conn = pymysql.connect(host='localhost',database='busdb',password='Sami@4998',user='root')
    return conn

import random
import string

def generate_unique_id(connection, table_name, column_name, length=12):
    
    #Generate a unique random string ID and ensure it does not exist in the database.

    characters = string.ascii_letters + string.digits

    while True:
        random_id = ''.join(random.choices(characters, k=length))

        query = f"SELECT 1 FROM `{table_name}` WHERE `{column_name}`=%s LIMIT 1"

        with connection.cursor() as cursor:
            cursor.execute(query, (random_id,))
            result = cursor.fetchone()

        if result is None:
            return random_id


def generate_qr_code(data_string):
    """
    Accepts a string, generates a QR code, saves it as 'string.jpg',
    and returns the absolute file path.
    """
    # 1. Clean the string to make it a safe filename (remove special characters)
    # We replace non-alphanumeric characters with underscores
    safe_filename = re.sub(r'[^\w\s-]', '', data_string).strip().replace(' ', '_')
    filename = f"static/{safe_filename}.jpg"
    
    # 2. Create the QR Code object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # 3. Add data and make the image
    qr.add_data(data_string)
    qr.make(fit=True)
    
    # Create an RGB image (standard for JPG)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    # 4. Save the image
    img.save(filename)
    
    # 5. Return the absolute path
    return os.path.abspath(filename)

# Example Usage:
# path = generate_qr_code("Bus-101-Ticket")
# print(f"QR Code saved at: {path}")
 
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
        cur.execute("SELECT * FROM tickets WHERE bus = %s",(ticketno,))
        data = cur.fetchone()
    return data

def tickets():
    with database_conn() as conn:
        cur = conn.cursor()
                # Get today's date in YYYY-MM-DD format
        today = datetime.today().strftime('%Y-%m-%d')

        # Your SQL execution
        query = "SELECT * FROM tickets WHERE addedon = %s"
        params = (today,)
        cur.execute(query,params)
        data = cur.fetchall()
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

def recharge_mock(userid,amount,tx_ref):
    if int(amount) >= 0:
        with database_conn() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO wallet VALUES (%s,%s,%s)",(tx_ref,amount,userid,))
            conn.commit()
        return True
    return False

def isticket_paid(userid):
    with database_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT paidby FROM payment WHERE paidby = %s",(userid,))
        data = cur.fetchone()
        return bool(data)

def paymentinfo(userid):
    with database_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM payment WHERE paidby = %s",(userid,))
        data = cur.fetchall()
    return data
    
def ticket_id(tickid):
    with database_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE ticketid = %s",(tickid,))
        data = cur.fetchone()
    return data

def payforticket(tx_ref,totalprice,tot_pers,paidby,ticket):
    with database_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO payment VALUES(%s,%s,%s,%s,%s)",(tx_ref,totalprice,tot_pers,paidby,ticket))
        conn.commit()
    return True

def is_transaction_new(tx_ref):
    # Check if this tx_ref already exists in the transactions table
    with database_conn() as cursor:
        cursor.execute("SELECT tx_ref FROM transactions WHERE tx_ref = %s", (tx_ref,))
        return cursor.fetchone()

def process_recharge(userid, amount, tx_ref):
    try:
        with database_conn() as conn:
            cursor = conn.cursor()
            # 1. Record the transaction so it can't be reused
            cursor.execute("INSERT INTO transactions (tx_ref, amount, userid) VALUES (%s, %s, %s)", 
                        (tx_ref, float(amount), userid))
            
            cursor.execute("SELECT current_balance FROM user_balance WHERE userid = %s",(userid,))
            
            if cursor.fetchone():
                data = cursor.fetchone()[0]
                amount =float(amount) + float(data)
            else:
                amount = float(amount)
            cursor.execute("""
                INSERT INTO user_balance (userid, current_balance) 
                VALUES (%s, %s)
            """, (userid, amount))
            conn.commit()
            return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

