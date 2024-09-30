import traceback


def fetch_id_from_payment(conn,table_name,user_id):
    cursor = conn.cursor()
    try:
        sql_query = f"""
        select course_id from {table_name} where user_id = %s
        """
        cursor.execute(sql_query,(user_id,))
        row = cursor.fetchall()
        if row:
            return row
        else:
            return None
    except Exception as ex:
        error_ex = traceback.format_exc()
        print(error_ex)
    finally:
        cursor.close()
