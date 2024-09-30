
def save_user_credintial_registerform(connection_pool,user_data,table_name):
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    try:
        insert_query = f"""
            INSERT INTO {table_name} (username, email, phone_number, password, encryption_password, town, city)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        hashed_password = user_data['password']  # Make sure this is hashed
        cursor.execute(insert_query, (
            user_data['username'],
            user_data['email'],
            user_data['phone_number'],
            hashed_password,
            user_data['encryption_password'],
            user_data['town'],
            user_data['city']
        ))
        conn.commit()
    except Exception as ex:
        print(ex)
    finally:
        cursor.close()