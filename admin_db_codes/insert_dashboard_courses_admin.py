import logging


def insert_dashboard_course(connection_pool, curriculum_data, table_name):
    connection = connection_pool.getconn()
    cursor = connection.cursor()
    try:
        insert_query = f"""
            INSERT INTO {table_name} (title, course_category, url)
            VALUES (%s, %s, %s)
        """

        cursor.execute(insert_query, (
            curriculum_data['title'],
            curriculum_data['course_category'],
            curriculum_data['image_url']
        ))

        connection.commit()
        print("Course inserted successfully.")

    except Exception as e:
        print("Error while inserting course:", e)
        logging.error(f"Database insert error: {e}")
        connection.rollback()  # Rollback on error

    finally:
        cursor.close()
        connection_pool.putconn(connection)
