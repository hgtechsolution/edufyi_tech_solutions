# Function to insert form data into the database
import psycopg2


def insert_course_video(conn,course_id, week_number, video_name, video_number, week_topic,table_name):
    try:

        cursor = conn.cursor()

        # SQL query to insert data into the course_video table
        insert_query = f"""
        INSERT INTO {table_name} (course_id, week_number, video_name, video_number, week_topic)
        VALUES (%s, %s, %s, %s, %s);
        """
        # Execute the query with the form data
        cursor.execute(insert_query, (course_id, week_number, video_name, video_number, week_topic))

        # Commit the transaction to save the data
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        # conn.close()

    except psycopg2.DatabaseError as error:
        print(f"Error inserting data into the database: {error}")
        if conn:
            conn.rollback()
