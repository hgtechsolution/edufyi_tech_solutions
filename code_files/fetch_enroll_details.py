import traceback

import psycopg2


def get_curriculum(course_name):
    global conn
    try:
        # Connect to the database
        conn = psycopg2.connect("dbname=edtech user=postgres password=123456789")
        cursor = conn.cursor()

        # Fetch the course data
        cursor.execute("SELECT * FROM course_curriculum WHERE course_name = %s ORDER BY id", (course_name,))
        result = cursor.fetchone()

        if result:
            # Get column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]

            # Create a dictionary by zipping column names and values
            course_data = dict(zip(column_names, result))

            conn.close()
            return course_data
        else:
            conn.close()
            return None
    except Exception as e:
        print(f"Error fetching curriculum: {e}")
        error_ex = traceback.format_exc()
        print(error_ex)
        if conn:
            conn.close()
        return None


def enrolled_course_get_curriculum(course_name):
    global conn
    try:
        # Connect to the database
        conn = psycopg2.connect("dbname=edtech user=postgres password=123456789")
        cursor = conn.cursor()

        # Fetch the course data
        cursor.execute("SELECT * FROM enrolled_course_curriculum WHERE course_name = %s ORDER BY id", (course_name,))
        result = cursor.fetchone()

        if result:
            # Get column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]

            # Create a dictionary by zipping column names and values
            course_data = dict(zip(column_names, result))

            conn.close()
            return course_data
        else:
            conn.close()
            return None
    except Exception as e:
        print(f"Error fetching curriculum: {e}")
        error_ex = traceback.format_exc()
        print(error_ex)
        if conn:
            conn.close()
        return None
