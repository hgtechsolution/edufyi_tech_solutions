def fetch_videoid_courseid_weekid(connection_pool, table_name, video_name):
    # Get a connection from the connection pool
    conn = connection_pool.getconn()
    cursor = conn.cursor()

    try:
        # SQL query to insert data into the specified table
        sql_query = f"""
           select id,course_id,week_number,video_number from {table_name}
           where video_name = %s
           """

        # Execute the query with the provided parameters
        cursor.execute(sql_query, (video_name,))

        row = cursor.fetchone()
        if row:
            video_id, course_id, week_number, video_number = row
            return video_id, course_id, week_number, video_number
        else:
            return None, None, None, None

    except Exception as ex:
        # Handle any exception and rollback the transaction if necessary
        conn.rollback()
        connection_pool.putconn(conn)
        print(f"Error: {ex}")
    finally:
        # Close the cursor and return the connection back to the pool
        cursor.close()
        connection_pool.putconn(conn)



