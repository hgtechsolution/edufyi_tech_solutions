def save_payment(conn, payment_record, table_name):
    cursor = conn.cursor()
    try:
        # Extract column names and corresponding values from payment_record dynamically
        columns = ', '.join(payment_record.keys())
        placeholders = ', '.join(['%s'] * len(payment_record))
        values = tuple(payment_record.values())

        # Construct the dynamic SQL query
        insert_query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
        """

        # Execute the query with dynamic values
        cursor.execute(insert_query, values)

        # Commit the transaction
        conn.commit()

        print("Payment record inserted successfully.")

    except Exception as e:
        print(f"Error occurred: {e}")
        if conn:
            conn.rollback()

    finally:
        # Close the cursor
        if cursor:
            cursor.close()
