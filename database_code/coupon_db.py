
def validate_coupon(connection_pool,coupon_code,table_name):
    # Establish a database connection
    conn = connection_pool.getconn()
    cursor = conn.cursor()

    # Query to get the discount for the given coupon code
    cursor.execute(f"""
        SELECT discount FROM {table_name}
        WHERE code = %s AND is_active = TRUE AND (expiry_date IS NULL OR expiry_date >= CURRENT_DATE);
    """, (coupon_code,))

    result = cursor.fetchone()
    cursor.close()
    connection_pool.putconn(conn)

    # Return discount if found, else return 0
    if result:
        return result[0]
    return None