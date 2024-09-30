from flask import flash, session, redirect, url_for
from models import User, bcrypt, db


def verify_otp_code_(stored_otp, entered_otp, new_password, email):
    # Verify OTP
    if stored_otp and int(entered_otp) == stored_otp:
        user = User.query.filter_by(email=email).first()
        if user:
            flash('OTP verified successfully. Your password has been reset.', 'success')

            # Hash the new password
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

            # Update the password in the database
            user.password = hashed_password
            db.session.commit()

            # Clear session
            session.pop('email', None)
            session.pop('stored_otp', None)
            session.pop('new_password', None)

            # Redirect to login page after successful OTP verification and password reset
            return redirect(url_for('login'))

        else:
            flash('User not found. Please check your email.', 'danger')
            return redirect(url_for('forgot_password'))

    else:
        flash('Invalid OTP. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))
