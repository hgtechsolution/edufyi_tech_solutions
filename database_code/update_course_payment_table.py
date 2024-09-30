def update_course_payment_db(conn, table_name, user_id, course_id, course_name,
                             course_category, amount, payment_status,
                             transaction_id, course_expire_date,
                             payment_id,order_id,signature):
    cursor = conn.cursor()
    try:
        # Check if the user has already purchased the course
        sql_query_search = f"""
        SELECT course_id, course_name 
        FROM {table_name} 
        WHERE user_id = %s AND course_name = %s
        """
        cursor.execute(sql_query_search, (user_id, course_name))
        row = cursor.fetchone()

        if row:
            # If the course exists and is expired, update the expiration date
            sql_update_query = f"""
            UPDATE {table_name} 
            SET course_expire_date = %s
            WHERE user_id = %s AND course_id = %s
            """
            cursor.execute(sql_update_query, (course_expire_date, user_id, course_id))
            conn.commit()
        else:
            # Insert a new record for the course purchase
            sql_query = f"""
            INSERT INTO {table_name} (user_id, course_id, course_name, course_category, 
            amount, payment_status, transaction_id, course_expire_date,
            payment_id,order_id,signature)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s)
            """
            cursor.execute(sql_query, (user_id, course_id, course_name, course_category,
                                       amount, payment_status, transaction_id,
                                       course_expire_date,payment_id,order_id,signature))
            conn.commit()

    except Exception as ex:
        # Log the exception (assumed you're using logging)
        print(f"Error: {ex}")
        # Optionally: raise ex to propagate the exception further
    finally:
        cursor.close()