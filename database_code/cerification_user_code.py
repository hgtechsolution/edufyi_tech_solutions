import logging
import pandas as pd

def send_certification_code(connection_pool, user_id, enrolled_course_curriculum_table_name,
                            enrolled_course_tracker_table,enrolled_course_video,course_name):
    connection = connection_pool.getconn()
    cursor = connection.cursor()
    try:
        # Step 1: Fetch id from the enrolled_course_curriculum table
        select_query_enrolled_course_curriculum = f"""
            SELECT id FROM {enrolled_course_curriculum_table_name}
            where course_name = %s
        """
        cursor.execute(select_query_enrolled_course_curriculum,(course_name,))
        row_id = cursor.fetchone()

        if row_id:
            course_id = row_id[0]

            # Query to fetch the user_enrolled_course_tracker table
            select_query_enrolled_course_tracker = f"""
                SELECT * FROM {enrolled_course_tracker_table}
                WHERE user_id = %s AND course_id = %s
            """
            cursor.execute(select_query_enrolled_course_tracker, (user_id, course_id))
            user_course_tracker = cursor.fetchall()

            if not user_course_tracker:
                print("No records found for the user in the course tracker.")
            else:
                # Get column names from the cursor description
                columns_tracker = [desc[0] for desc in cursor.description]
                # Convert the fetched data into a dictionary and then to a DataFrame
                df_user_course_tracker = pd.DataFrame(user_course_tracker, columns=columns_tracker)

                # Query to fetch course videos
                select_query_course_video = f"""
                    SELECT * FROM {enrolled_course_video}
                    WHERE course_id = %s
                """
                cursor.execute(select_query_course_video, (course_id,))
                course_videos = cursor.fetchall()

                if not course_videos:
                    print("No course videos found.")
                else:
                    # Get column names and create DataFrame for course videos
                    columns_video = [desc[0] for desc in cursor.description]
                    df_course_video = pd.DataFrame(course_videos, columns=columns_video)

                    # Condition to find videos left for certification
                    df_number_videos_left = df_course_video[
                        ~df_course_video['video_number'].isin(df_user_course_tracker['video_id'].to_list())
                    ]
                    if df_number_videos_left.empty:
                        return None
                    else:
                        number_week_list = list(set(df_number_videos_left['week_number'].to_list()))
                        if not  number_week_list:
                            #create a certificate here
                            return None
                        else:
                            return number_week_list



                    print(f"Videos left for certification: {df_number_videos_left}")


    except Exception as e:
        print("Error while processing:", e)
        logging.error(f"Database error: {e}")
        connection.rollback()  # Rollback on error

    finally:
        cursor.close()
        connection_pool.putconn(connection)
