from code_files.sending_payment_recipt import \
    registration_transaction_receipt_format, send_payment_receipt
from database_code.fetch_user_name_email import fetch_user_email_db


def send_user_registration_payment(User,connection_pool,payment_data,user_data):
    user = User.query.filter_by(email=user_data['email']).first()
    # the email template data
    receipt_content = registration_transaction_receipt_format(user.username,
                                                              payment_data)

    # sending a receipt to client
    name, email, phone_number = fetch_user_email_db(
        connection_pool, table_name='users',
        id=user.id)
    send_payment_receipt(receipt_content, email, 'Course Registration')
