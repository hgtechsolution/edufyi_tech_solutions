from database_code.save_recipt_user import save_payment
from database_code.save_transaction import insert_transaction_data
from datetime import datetime,timedelta

def save_user_register_payments(conn,User,user_data,payment_data,payment_record):
    user = User.query.filter_by(email=user_data['email']).first()

    # converting paise to rupee for transaction table
    amount = payment_data['amount'] / 100
    payment_data['amount'] = amount

    # inserting a row for registration transactions table
    payment_data.update({'user_id': user.id})
    transaction_id = insert_transaction_data(conn,
                                             'registration_transactions',
                                             payment_data, user.id)

    # saving details for the registration payment
    current_time = datetime.now()
    registration_expiry_date = current_time + timedelta(days=1)
    payment_record.update({'user_id': user.id})
    payment_record.update({'transaction_id': transaction_id})
    payment_record.update(
        {'registration_expiry_time': registration_expiry_date})
    # insert transaction receipt
    save_payment(conn, payment_record, 'registration_payment')