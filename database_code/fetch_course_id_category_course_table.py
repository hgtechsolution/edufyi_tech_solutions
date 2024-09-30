def fetch_course_id_category(conn, table_name, course_name):
    cur = conn.cursor()
    try:
        sql_query = f"""
        SELECT id, course_category FROM {table_name} WHERE title = %s
        """
        cur.execute(sql_query, (course_name,))
        row = cur.fetchone()  # Correctly using cur.fetchone()

        if row:
            id, course_category = row
            return id, course_category
        else:
            print(f"No course found with name: {course_name}")
            return None, None
    except Exception as ex:
        print(f"An error occurred: {ex}")
        return None, None
    finally:
        cur.close()
