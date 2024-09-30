from code_files.sending_payment_recipt import \
    course_transaction_receipt_format, send_payment_receipt
from database_code.fetch_user_name_email import fetch_user_email_db


def send_user_course_transaction_receipt(connection_pool,user_id,course_name,payment_data):
    name, email, phone_number = fetch_user_email_db(
        connection_pool, table_name='users',
        id=user_id)
    # the email template data
    receipt_content = course_transaction_receipt_format(name,
                                                        course_name,
                                                        payment_data)

    send_payment_receipt(receipt_content, email, course_name)