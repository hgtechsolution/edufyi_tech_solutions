def fetch_user_email_db(connection_pool, table_name, id):
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    try:
        sql_query = f"SELECT username,email,phone_number FROM {table_name} WHERE id = %s"
        cursor.execute(sql_query, (id,))
        row = cursor.fetchone()

        if row and row[0]:
            name = row[0]
            email = row[1]
            phone_number = row[2]

            return name,email,phone_number
        else:
            return None
    finally:
        cursor.close()
        connection_pool.putconn(conn)
