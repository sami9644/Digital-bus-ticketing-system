import pymysql

def run_mysql_file(host, user, password, database, sql_file):
    connection = None
    try:
        # 1. Connect to the database
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            autocommit=True # Automatically commits changes
        )

        with connection.cursor() as cursor:
            # 2. Read the SQL file
            with open(sql_file, 'r') as file:
                sql_script = file.read()

            # 3. Execute the script
            # Note: PyMySQL can execute multiple statements if 
            # client_flag=CLIENT.MULTI_STATEMENTS is set, 
            # but usually, it's safer to split by semicolon if simple.
            
            # Simple approach: Split by semicolon (works for basic scripts)
            commands = sql_script.split(';')
            
            for command in commands:
                if command.strip():
                    cursor.execute(command)
            
        print(f"Successfully executed {sql_file}")

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if connection:
            connection.close()

# Usage
run_mysql_file('localhost', 'root', 'Sami@4998','busdb' ,'ticket.sql')