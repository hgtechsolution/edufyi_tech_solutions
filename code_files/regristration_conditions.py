import traceback
from datetime import datetime

def extract_regristration_expire_date_db(conn,table_name,user_id):
    cursor = conn.cursor()
    try:
        sql_query = f"""
        select registration_expiry_time from {table_name}
        where user_id = %s
        """
        cursor.execute(sql_query,(user_id,))
        row = cursor.fetchone()
        if row:
            if row[0]:
                registration_expiry_time = row[0]
                return registration_expiry_time

        return False
    except Exception as ex:
        print(ex)
    finally:
        cursor.close()


def fetch_course_purchased_db(conn,table_name,user_id):
    cursor = conn.cursor()
    try:
        sql_query = f"""
        select * from {table_name}
        where user_id = %s
        """
        cursor.execute(sql_query,(user_id,))
        row = cursor.fetchone()
        if row[0]:
            return True
        else:
            return False
    except Exception as ex:
        error_ex = traceback.format_exc()
        print(error_ex)
    finally:
        cursor.close()

def regristration_conditions_db(connection_pool, regristration_payment_table_name,course_payment_tractions_table_name, user_id):
    conn = connection_pool.getconn()
    # fetch registration expiry date
    registration_expiry_time = extract_regristration_expire_date_db(conn, regristration_payment_table_name, user_id)

    if registration_expiry_time:
        # fetch course transaction table
        bool_course_trans = fetch_course_purchased_db(conn, course_payment_tractions_table_name, user_id)

        connection_pool.putconn(conn)
        current_time = datetime.now()
        # val = current_time< registration_expiry_time
        if current_time < registration_expiry_time and bool_course_trans == False:
            return True
        elif current_time < registration_expiry_time or bool_course_trans == True:
            return True
        else:
            return False
    else:
        return False
