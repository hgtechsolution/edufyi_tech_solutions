def insert_user_enrolledcourse_ttracker(connection_pool, table_name, user_id,
                                        course_id,
                                        week_number, video_id, status):
    # Get a connection from the connection pool
    conn = connection_pool.getconn()
    cursor = conn.cursor()

    try:
        # SQL query to check if the record already exists
        check_the_record_is_present = f"""
        SELECT * FROM public.{table_name}
            WHERE user_id = %s AND course_id = %s AND week_number = %s AND video_id = %s
            ORDER BY id ASC; 
        """
        cursor.execute(check_the_record_is_present, (
            user_id, course_id, week_number, video_id))

        row = cursor.fetchone()

        if row is None:
            # Record doesn't exist, insert a new one
            sql_query = f"""
            INSERT INTO {table_name} (user_id, course_id, week_number, video_id, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_query, (
                user_id, course_id, week_number, video_id, status))
            conn.commit()  # Commit only if the insertion is successful
            print("Course status has been inserted successfully.")
        else:
            # Record exists, no need to insert
            print("Course status is already updated.")

    except Exception as ex:
        # Rollback the transaction in case of an error
        conn.rollback()
        print(f"Error: {ex}")

    finally:
        # Close the cursor and return the connection to the pool
        cursor.close()

        connection_pool.putconn(conn)
