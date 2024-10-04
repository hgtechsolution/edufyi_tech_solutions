import psycopg2
import json

def insert_enrolled_course(connection_pool, curriculum_data, table_name):
    connection = connection_pool.getconn()
    cursor = connection.cursor()
    try:
        # Prepare the columns and values for insertion
        course_columns = [key for key in curriculum_data]
        course_values = [
            json.dumps(curriculum_data[key]) if isinstance(curriculum_data[key], (dict, list)) else curriculum_data[key]
            for key in course_columns
        ]

        # Construct the SQL query dynamically
        course_insert_query = f"""
        INSERT INTO {table_name} ({', '.join(course_columns)}) 
        VALUES ({', '.join(['%s'] * len(course_values))})
        """

        # Execute the insert and retrieve the course id
        cursor.execute(course_insert_query, course_values)
        # course_id = cursor.fetchone()[0]

        # Commit the transaction
        connection.commit()
        # return course_id

    except psycopg2.Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection_pool.putconn(connection)
