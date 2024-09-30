import json
from datetime import datetime

def insert_transaction_data(conn, table_name, data,user_id):
    cursor = conn.cursor()
    try:
        if 'created_at' in data and isinstance(data['created_at'], int):
            data['created_at'] = datetime.fromtimestamp(data['created_at'])
        # Define SQL query dynamically based on the table name
        data.update({'payment_id': str(data['id'])})
        columns = list(data.keys())
        columns = columns[1:]
        # columns.insert(0,'payment_id')




        values_placeholders = ', '.join(['%s'] * len(columns))  # Corrected placeholder generation
        columns_str = ', '.join(columns)

        insert_query = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES ({values_placeholders})
            RETURNING id;
        """

        # Extract values in the order of columns
        values = tuple(
            json.dumps(value) if isinstance(value, (dict, list)) else value
            for value in (data[col] for col in columns)
        )

        cursor.execute(insert_query, values)
        conn.commit()
        row = cursor.fetchone()[0]
        print("Transaction Data inserted successfully")

        # extract traction id from user id
        # sql_query_extract_id = f"""
        # select id from {table_name}
        # where user_id = %s
        # # """
        # cursor.execute(sql_query_extract_id,(user_id,))
        # row = cursor.fetchone()
        return row
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()
