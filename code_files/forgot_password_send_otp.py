from random import randint
from flask import session
from flask_mail import Message
from models import User

def send_otp(mail,email, otp):
    msg = Message('Your OTP for Password Reset', sender='scarlet@epicculinaryexperiences.com', recipients=[email])
    msg.body = f'Your OTP is: {otp}'
    mail.send(msg)

def forget_password_send_otp_code(mail,email, new_password):
    # Check if email exists in the database
    user = User.query.filter_by(email=email).first()
    if user:
        # Generate and store OTP
        otp = randint(1000, 9999)
        session['id'] = user.id
        session['stored_otp'] = otp
        session['new_password'] = new_password
        session['email'] = email
        # Send OTP via email
        send_otp(mail,email, otp)
        return True
    else:
        return False
