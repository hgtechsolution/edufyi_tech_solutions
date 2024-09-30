from database_code.fetch_course_id_category_course_table import \
    fetch_course_id_category
from database_code.save_transaction import insert_transaction_data
from datetime import datetime,timedelta

from database_code.update_course_payment_table import update_course_payment_db


def save_user_course_transaction_details_client(conn,payment_data,user_id,course_name,payment_record):
    # converting paise to rupee for transaction table
    amount = payment_data['amount'] / 100
    payment_data['amount'] = amount

    # adding user id for the transaction table
    payment_data.update({'user_id': user_id})
    transaction_id = insert_transaction_data(conn,
                                             'course_transactions',
                                             payment_data, user_id)

    # fetching course category and course id to insert in course payment table
    course_id, course_category = fetch_course_id_category(conn,
                                                          'course',
                                                          course_name)

    # adding expiry time to the courses
    current_time = datetime.now()
    future_time = current_time + timedelta(days=60)

    # updating the course payment table
    update_course_payment_db(conn, 'course_payments', user_id,
                             course_id, course_name,
                             course_category,
                             payment_record['amount'],
                             payment_record['status'],
                             transaction_id, future_time,
                             payment_record['payment_id'],
                             payment_record['order_id'],
                             payment_record['signature'])