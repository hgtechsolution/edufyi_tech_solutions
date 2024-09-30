import logging
import traceback
from datetime import datetime, timedelta
import os
from doctest import debug

from werkzeug.utils import secure_filename
from b2sdk.v2 import InMemoryAccountInfo
from b2sdk.v2 import B2Api
from psycopg2 import pool

import psycopg2
import razorpay
from flask_mail import Mail, Message
from flask import Flask, render_template, url_for, flash, redirect, session, request, jsonify, make_response

from admin_db_codes.insert_curriculum_data import insert_course
from admin_db_codes.insert_dashboard_courses_admin import insert_dashboard_course
from code_files.forgot_password_send_otp import forget_password_send_otp_code
from code_files.regristration_conditions import regristration_conditions_db
from code_files.save_user_courese_transactions_details import save_user_course_transaction_details_client
from code_files.save_user_regristration_code import save_user_register_payments
from code_files.send_user_regristration_recipt_code import send_user_registration_payment
from code_files.verify_otp_code import verify_otp_code_
from code_files.fetch_enroll_details import get_curriculum, enrolled_course_get_curriculum
from config import Config
from database_code.cerification_user_code import send_certification_code
from database_code.coupon_db import validate_coupon
from database_code.enrolled_course_fetch_courseidfrompayment import fetch_id_from_payment
from database_code.fetch_course_id_category_course_table import fetch_course_id_category
from database_code.fetch_user_name_email import fetch_user_email_db
from database_code.fetch_video_id_course_id_week_id import fetch_videoid_courseid_weekid
from database_code.insert_dashboard_courses_admin import insert_user_enrolledcourse_ttracker
from database_code.save_recipt_user import save_payment
from database_code.save_transaction import insert_transaction_data
from database_code.save_user_credintials_db import save_user_credintial_registerform
from database_code.update_course_payment_table import update_course_payment_db
from models import db, bcrypt, User, Encry_Key, Course, Admin
from forms import RegistrationForm, LoginForm, VideoUploadForm, OTPVerificationForm, ForgotPasswordForm, PaymentForm, \
    AdminLoginForm, AdminRegistrationForm, CoursePage, CurriculumForm
from password_encryption import encrypt_message
from send_user_course_recipt_to_client import send_user_course_transaction_receipt

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Create the upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,  # Minimum number of connections
    maxconn=10,  # Maximum number of connections
    user='postgres',
    password='123456789',
    host='localhost',
    port='5432',
    database='edtech'
)

client = razorpay.Client(auth=("rzp_test_q41WR8T1FOwyUT", "lzwIH6bjKMMOiMwRxvM8oyMj"))

def connect_to_backblaze():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    # Replace with your Backblaze credentials
    application_key_id = '8130bde3acb8'
    application_key = '00549b8c2019a7ca5de9184fb4d63c1f5c1b4638cb'
    b2_api.authorize_account('production', application_key_id, application_key)
    return b2_api

def get_file_url(b2_api, bucket_name, file_name):
    # Access the bucket
    bucket = b2_api.get_bucket_by_name(bucket_name)

    # Generate the authorized download URL for the private file
    # Get the download authorization token for the file
    authorization_token = bucket.get_download_authorization(file_name, 3600)  # 1 hour valid token

    # authorization_token = bucket.get_download_authorization(file_name,
    #                                                         3600)  # 1 hour valid token
    base_download_url = b2_api.get_download_url_for_file_name(bucket_name,
                                                              file_name)
    file_url = f"{base_download_url}?Authorization={authorization_token}"
    return file_url


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

mail = Mail(app)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Encrypt password
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')

        # password is encrypted and store in db
        key = Encry_Key.query.filter_by(key_type='password').first()
        ency_password = encrypt_message(key.key, form.password.data)

        # Temporarily store user data in session for the registration payment
        session['user_data'] = {
            'username': form.username.data,
            'email': form.email.data,
            'phone_number': form.phone_number.data,
            'password': hashed_password,
            'encryption_password': ency_password,
            'town': form.town.data,
            'city': form.city.data
        }

        # Redirect to the payment confirmation page
        return redirect(
            url_for('registration_fee', user_name=form.username.data,
                    email=form.email.data,
                    phone_number=form.phone_number.data))

    return render_template('register.html', form=form)


@app.route('/registration_fee/<user_name>/<email>/<phone_number>',
           methods=['GET', 'POST'])
def registration_fee(user_name, email, phone_number):
    amount = 1000  # Default registration fee

    try:
        # creating a order for the razerpay
        key = 'rzp_test_q41WR8T1FOwyUT'
        data = {
            "amount": amount * 100,  # amount in paise
            "currency": "INR",
            "receipt": f"order_{user_name}",
            "payment_capture": 1
        }
        payment = client.order.create(data=data)

        # for send the data to razerpay api
        pdata = [key, amount * 100, payment["id"]]

    except Exception as e:
        # Log the error and display a user-friendly message
        print(f"Error creating order: {str(e)}")
        flash("Error processing payment. Please try again later.")
        error_ex = traceback.format_exc()
        print(error_ex)
        return redirect(url_for('register'))

    return render_template('registration_payment_form.html', amount=amount,
                           user_name=user_name, email=email,
                           phone_number=phone_number, pdata=pdata, key=key)



@app.route('/register_payment_done', methods=['POST'])
def register_payment_done():
    # creating db connection to store the payment details
    conn = connection_pool.getconn()
    pid = request.form.get("razorpay_payment_id")
    ordid = request.form.get("razorpay_order_id")
    sign = request.form.get("razorpay_signature")

    if not pid:
        return "Payment failed. No payment ID received.", 400

    params = {
        'razorpay_order_id': ordid,
        'razorpay_payment_id': pid,
        'razorpay_signature': sign
    }

    try:
        # Verify the signature
        final = client.utility.verify_payment_signature(params)

        if final:
            # Fetch transaction details from Razorpay
            payment_data = client.payment.fetch(pid)
            # print(payment_data)

            # Save payment details to the database
            payment_record = {
                'amount': payment_data['amount'] / 100,
                # converting back from paise to INR
                'payment_id': pid,
                'order_id': ordid,
                'signature': sign,
                'status': 'completed'  # or fetch from payment_data if needed
            }
            # Retrieve user data from session and create a new user if necessary
            user_data = session.pop('user_data', None)
            if not user_data:
                return "Session expired or invalid user data.", 400

            # Fetch user from the database
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                save_user_credintial_registerform(connection_pool, user_data,
                                                  'users')

            # save user register transaction details and recipt
            save_user_register_payments(conn, User, user_data, payment_data,
                               payment_record)

            # send transaction receipt email to client
            send_user_registration_payment(User, connection_pool, payment_data, user_data)

            flash(
                'Your payment was successful and your account has been created!',
                'success')

            connection_pool.putconn(conn)

            # Redirect to a confirmation or homepage
            return redirect("/", code=301)

        else:
            connection_pool.putconn(conn)
            return "Payment verification failed. Please try again.", 400



    except razorpay.errors.SignatureVerificationError:
        connection_pool.putconn(conn)
        error_ex = traceback.format_exc()
        print(error_ex)
        return "Signature verification failed. Possible fraudulent payment.", 400


    except Exception as e:
        # print(f"Error: {e}")
        connection_pool.putconn(conn)
        error_ex = traceback.format_exc()
        print(error_ex)
        return "Signature verification failed. Possible fraudulent payment.", 500




@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            bool_val_registration_cond = regristration_conditions_db(
                connection_pool, 'registration_payment',
                'registration_transactions',
                user.id)
            if bool_val_registration_cond == False:
                flash(
                    'Regristration Is Expired, Please Register Again And Purchase Courses')
                return redirect(url_for('register'))

            # Create a response object
            response = make_response(redirect(url_for('dashboard_courses')))

            # Set the cookie with an expiration time of 1 week (in seconds)
            response.set_cookie('user_id', f'{user.id}',
                                max_age=7 * 24 * 60 * 60)

            return response
        else:
            flash('Login Unsuccessful. Please check email and password',
                  'danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
def dashboard_courses():
    # reading the stored cookie
    user_id = request.cookies.get('user_id')
    if user_id is not None:
        # registration login
        bool_val_registration_cond = regristration_conditions_db(
            connection_pool,
            'registration_payment',
            'registration_transactions',
            user_id)
        if bool_val_registration_cond == False:
            flash(
                'Regristration Is Expired, Please Register Again And Purchase Courses')
            return redirect(url_for('register'))
        session['id'] = user_id
        search_query = request.args.get('search','')  # Get the search query from the URL

        b2_api = connect_to_backblaze()
        # image_file_name = 'course_images/ai.jpg'
        image_bucket_name = 'course-images-dashboard'

        if search_query:
            # Filter courses based on the search term
            image_query = Course.query.filter(
                Course.title.ilike(f'%{search_query}%')).all()

            # images = [{'title': course.title,
            #            'url': url_for('static', filename=f'{course.url}')} for
            #           course in image_query]


            images = [{'title': course.title,
                       'url': get_file_url(b2_api, image_bucket_name, f'course_images/{course.url}')} for course in image_query]

            return render_template('course.html', images=images)

        else:
            # Fetch all courses if no search query is provided
            # image_query = Course.query.all()

            # Prepare a list of dictionaries with titles and image URLs

            technical = Course.query.filter_by(course_category='technical').all()
            technical_courses = [{'title': course.title,
                                  'url': get_file_url(b2_api, image_bucket_name, f'course_images/{course.url}')} for
                                 course in technical]

            non_technical = Course.query.filter_by(course_category='non_technical').all()
            non_technicals = [{'title': course.title,
                               'url': get_file_url(b2_api, image_bucket_name, f'course_images/{course.url}')} for
                              course in non_technical]

            live_session = Course.query.filter_by(course_category='live_session').all()
            live_sessions = [{'title': course.title,
                              'url': get_file_url(b2_api, image_bucket_name, f'course_images/{course.url}')} for
                             course in live_session]

    else:
        flash('Session Has Expired, Please Login Again')
        return redirect(url_for('login'))
    return render_template('course.html', technical_courses=technical_courses, non_technicals=non_technicals,live_sessions=live_sessions)


@app.route('/admin_dashboard')
def admin_dashboard():
    # reading the stored cookie
    user_id = request.cookies.get('user_id')
    if user_id is not None:

        session['id'] = user_id
        search_query = request.args.get('search','')  # Get the search query from the URL

        b2_api = connect_to_backblaze()
        # image_file_name = 'course_images/ai.jpg'
        image_bucket_name = 'course-images-dashboard'

        if search_query:
            # Filter courses based on the search term
            image_query = Course.query.filter(
                Course.title.ilike(f'%{search_query}%')).all()

            images = [{'title': course.title,
                       'url': url_for('static', filename=f'{course.url}')} for
                      course in image_query]

            return render_template('admin_dashboard.html', images=images)

        else:
            # Fetch all courses if no search query is provided
            # image_query = Course.query.all()

            # Prepare a list of dictionaries with titles and image URLs

            technical = Course.query.filter_by(course_category='technical').all()
            technical_courses = [{'title': course.title,
                                  'url': get_file_url(b2_api, image_bucket_name, f'course_images/{course.url}')} for
                                 course in technical]

            non_technical = Course.query.filter_by(course_category='non_technical').all()
            non_technicals = [{'title': course.title,
                               'url': get_file_url(b2_api, image_bucket_name, f'course_images/{course.url}')} for
                              course in non_technical]

            live_session = Course.query.filter_by(course_category='live_session').all()
            live_sessions = [{'title': course.title,
                              'url': get_file_url(b2_api, image_bucket_name, f'course_images/{course.url}')} for
                             course in live_session]

    else:
        flash('Session Has Expired, Please Login Again')
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', technical_courses=technical_courses, non_technicals=non_technicals,live_sessions=live_sessions)


@app.route('/enroll_course/<course_name>')
def enroll_course_page(course_name):
    # reading the stored cookie
    user_id = request.cookies.get('user_id')
    if user_id is not None:
        # registration login
        bool_val_registration_cond = regristration_conditions_db(
            connection_pool,
            'registration_payment',
            'registration_transactions',
            user_id)
        if bool_val_registration_cond == False:
            flash(
                'Registration is expired, please register again and purchase courses.')
            return redirect(url_for('register'))

        data = get_curriculum(course_name)
        b2_api = connect_to_backblaze()
        # image_file_name = 'course_images/ai.jpg'
        demo_video_bucket_name = 'demo-videos-enroll-course'
        banner_images_bucket_name = 'course-images-dashboard'

        if data is None:
            return "Course not found or error retrieving course details.", 404

        curriculum_weeks = data.get('curriculum', {}).get('weeks', [])
        for week in curriculum_weeks:
            topics = week['topics'][0].split(',')
            week['topics'] = topics

        print(curriculum_weeks)

        overview = data.get('overview')
        price = data.get('price')
        level = data.get('level')
        duration = data.get('duration')
        lessons = data.get('lessons')
        quizzes = data.get('quizzes')
        certifications = data.get('certifications')
        demo_video = get_file_url(b2_api, demo_video_bucket_name, f'demo_videos/{data.get('demo_video')}')
        # banner_image = data.get('banner_image')
        banner_image = get_file_url(b2_api, banner_images_bucket_name, f'banner_images/{data.get('banner_image')}')
        print(demo_video,banner_image)

        return render_template('enroll.html', curriculum=curriculum_weeks,
                               overviews=overview,
                               course_name=course_name, price=price,
                               level=level, duration=duration, lessons=lessons,
                               quizzes=quizzes,
                               certifications=certifications, demo_video=demo_video, banner_image=banner_image)
    flash('Session has expired, please login again.')
    return redirect(url_for('login'))


# enrolled courses Dashboard
@app.route('/dashboard_enrolled_courses')
def dashboard_enrolled_courses():
    # reading the stored cookie
    user_id = request.cookies.get('user_id')
    b2_api = connect_to_backblaze()
    # image_file_name = 'course_images/ai.jpg'
    image_bucket_name = 'course-images-dashboard'

    if user_id is not None:
        # registration login
        bool_val_registration_cond = regristration_conditions_db(
            connection_pool,
            'registration_payment',
            'registration_transactions',
            user_id)
        if bool_val_registration_cond == False:
            flash('Regristration Is Expired, Please Register Again And Purchase Courses')
            return redirect(url_for('register'))

        # fetch course id from the course payment table
        conn = connection_pool.getconn()
        course_ids = fetch_id_from_payment(conn,'course_payments',user_id)
        connection_pool.putconn(conn)

        technical_courses = []
        non_technicals_courses = []
        live_session_course = []
        if course_ids is None or not course_ids:
            return render_template('enrolled_dashboard.html', technical_courses=technical_courses,
                                   non_technicals=non_technicals_courses,
                                   live_sessions=live_session_course)
            # return flash("Purchase Courses From Dashboard")

        for course_id in course_ids:
            technical = Course.query.filter_by(id=course_id[0]).first()
            if technical.course_category == 'technical':
                technical_courses.append({'title': technical.title,
                                          'url': get_file_url(b2_api, image_bucket_name, f'course_images/{technical.url}')})

            non_technical = Course.query.filter_by(id=course_id[0]).first()
            if non_technical.course_category == 'non_technical':
                non_technicals_courses.append({'title': non_technical.title,
                                               'url': get_file_url(b2_api, image_bucket_name, f'course_images/{non_technical.url}')})

            # live_session = Course.query.filter_by(id=course_id[0]).first()
            # if live_session.course_category == 'live_session':
            #     live_session_course.append({'title': live_session.title,
            #                                 'url': get_file_url(b2_api, image_bucket_name, f'course_images/{course.url}')})

    else:
        flash('Session Has Expired, Please Login Again')
        return redirect(url_for('login'))
    return render_template('enrolled_dashboard.html', technical_courses=technical_courses, non_technicals=non_technicals_courses,
                           live_sessions=live_session_course)


@app.route('/enrolled_course/<course_name>')
def enrolled_course_page(course_name):
    # Reading the stored cookie
    user_id = request.cookies.get('user_id')
    if user_id is not None:
        # Registration login
        bool_val_registration_cond = regristration_conditions_db(
            connection_pool,
            'registration_payment',
            'registration_transactions',
            user_id
        )
        if not bool_val_registration_cond:
            flash('Registration Is Expired, Please Register Again And Purchase Courses')
            return redirect(url_for('register'))
        data = enrolled_course_get_curriculum(course_name)
        b2_api = connect_to_backblaze()
        # image_file_name = 'course_images/ai.jpg'
        demo_video_bucket_name = 'demo-videos-enroll-course'
        banner_images_bucket_name = 'course-images-dashboard'

        if data is None:
            return "Course not found or error retrieving course details.", 404

        curriculum_weeks = data.get('curriculum', {}).get('weeks', [])
        for week in curriculum_weeks:
            topics = week['topics'][0].split(',')
            videos = week['videos'][0].split(',')
            week['topics_videos'] = list(zip(topics, videos))  # Correctly update the week dictionary

        # Extract additional course details
        overview = data.get('overview')
        price = data.get('price')
        level = data.get('level')
        duration = data.get('duration')
        lessons = data.get('lessons')
        quizzes = data.get('quizzes')
        certifications = data.get('certifications')
        demo_video = get_file_url(b2_api, demo_video_bucket_name, f'demo_videos/{data.get('demo_video')}')
        # banner_image = data.get('banner_image')
        banner_image = get_file_url(b2_api, banner_images_bucket_name, f'banner_images/{data.get('banner_image')}')
        print(demo_video, banner_image)

        # Handle form submission for downloading certificate


        return render_template('enrolled_course_page.html',
                               curriculum=curriculum_weeks,
                               overview=overview,
                               course_name=course_name,
                               price=price,
                               level=level,
                               duration=duration,
                               lessons=lessons,
                               quizzes=quizzes,
                               certifications=certifications,demo_video=demo_video,banner_image=banner_image)
    flash('Session Has Expired, Please Login Again')
    return redirect(url_for('login'))


@app.route('/video_page/<course_name>/<week_topic_name>/<course_topic>/<video_file>',methods=['GET', 'POST'])
def video_page(course_name, week_topic_name, course_topic, video_file):
    # Reading the stored cookie
    user_id = request.cookies.get('user_id')

    if user_id is None:
        # Redirect to login if user is not logged in
        return redirect(url_for('login'))

    # Registration check
    bool_val_registration_cond = regristration_conditions_db(
        connection_pool,
        'registration_payment',
        'registration_transactions',
        user_id
    )

    if not bool_val_registration_cond:
        flash(
            'Registration is expired. Please register again and purchase courses.')
        return redirect(url_for('register'))

    # Fetch video, course, and week details
    video_id, course_id, week_number, video_number = fetch_videoid_courseid_weekid(
        connection_pool, 'course_videos', video_file
    )

    if not video_id:
        # Raise 404 if the video doesn't exist
        print('error')
        # abort(404, description="Video not found")

    if request.method == 'POST':
        # Mark the video as complete for the user
        insert_user_enrolledcourse_ttracker(
            connection_pool,
            'user_enrolled_course_tracker',
            user_id,
            course_id,
            week_number,
            video_number,
            status=True
        )
        flash('Video marked as complete.')

    b2_api = connect_to_backblaze()
    video_url = get_file_url(b2_api, 'course-videos-edutech', f'course_videos/{video_file}')
    # Render video page
    return render_template(
        'video_file.html',
        video_file=video_url,
        course_name=course_name,
        week_topic_name=week_topic_name,
        course_topic=course_topic
    )


@app.route('/certificate/<course_name>', methods=['GET', 'POST'])
def certificate(course_name):
    # Reading the stored cookie
    user_id = request.cookies.get('user_id')
    if user_id is not None:
        # Registration login
        bool_val_registration_cond = regristration_conditions_db(
            connection_pool,
            'registration_payment',
            'registration_transactions',
            user_id
        )
        if not bool_val_registration_cond:
            flash(
                'Registration Is Expired, Please Register Again And Purchase Courses')
            return redirect(url_for('register'))
        # form = CertificationForm()
        #
        # if form.validate_on_submit():
            # send the cerification to their mail

        week_number = send_certification_code(connection_pool, user_id,
                                'enrolled_course_curriculum',
                                'user_enrolled_course_tracker',
                                'course_videos',course_name)
        if week_number:
            flash(f'Please complete Course {course_name} Week {week_number} Videos')
        else:
            flash('Certificate successfully Sent To Your Email!')

    return render_template('certificate.html')




@app.route('/course_payment/<course_name>/<price>', methods=['GET', 'POST'])
def course_payment(course_name, price):
    user_id = request.cookies.get('user_id')
    if user_id is not None:
        session['course_name'] = course_name
        name, email,phone_number = fetch_user_email_db(connection_pool, table_name='users',
                                          id=user_id)
        form = PaymentForm()
        amount = float(price)

        if form.validate_on_submit():
            coupon = form.coupon.data  # Use the current form instance

            if coupon:
                # Validate coupon and apply discount
                discount = validate_coupon(connection_pool, coupon,
                                           table_name='coupons')
                if discount:
                    discount = float(discount)
                    # Apply the discount and update amount
                    amount = int(
                        (float(price) - (discount / 100) * float(price)))
                    flash(
                        f'Coupon applied! {discount}% discount applied. You have to pay {amount}',
                        'success')
                else:
                    # Invalid coupon
                    flash('Coupon is invalid', 'danger')
                # Create payment order with Razorpay
        key = 'rzp_test_q41WR8T1FOwyUT'
        data = {
            "amount": amount * 100,  # amount in paise
            "currency": "INR",
            "receipt": "order_rcptid_11",
            "payment_capture": 1
        }
        payment = client.order.create(data=data)  # Create the order
        pdata = [key, amount * 100,
                 payment["id"]]
    else:
        return redirect(url_for('login'))


    # Render the form with updated amount
    return render_template('course_payment_form.html', form=form,
                           amount=amount,
                           course_name=course_name, email=email, name=name,phone_number= phone_number,
                           pdata=pdata)


@app.route('/payment_confirmation', methods=['POST', 'GET'])
def payment_confirmation():
    conn = connection_pool.getconn()

    try:
        user_id = request.cookies.get('user_id')
        if user_id is not None:
            course_name = session['course_name']
            # course_name = 'Artificial Intelligence & Machine Learning'
            pid = request.form.get("razorpay_payment_id")
            ordid = request.form.get("razorpay_order_id")
            sign = request.form.get("razorpay_signature")

            if not pid:
                connection_pool.putconn(conn)
                return "Payment failed. No payment ID received.", 400

            params = {
                'razorpay_order_id': ordid,
                'razorpay_payment_id': pid,
                'razorpay_signature': sign
            }
            final = client.utility.verify_payment_signature(params)

            if final:
                payment_data = client.payment.fetch(pid)
                # print(payment_data)

                payment_record = {
                    'amount': payment_data['amount'] / 100,
                    'payment_id': pid,
                    'order_id': ordid,
                    'signature': sign,
                    'status': 'completed'
                }

                # user_id = session['id']

                # save the user course transaction details
                save_user_course_transaction_details_client(conn, payment_data,
                                                            user_id,
                                                            course_name,
                                                            payment_record)

                # sending a receipt to client
                send_user_course_transaction_receipt(connection_pool, user_id,
                                                     course_name, payment_data)

                connection_pool.putconn(conn)

                return redirect(url_for('dashboard_enrolled_courses')) #here add enrolled courses dashboard

            else:
                connection_pool.putconn(conn)
                return "Signature verification failed. Possible fraudulent payment.", 400

        else:
            connection_pool.putconn(conn)
            return redirect(url_for('login'))

    except razorpay.errors.SignatureVerificationError:
        connection_pool.putconn(conn)
        error_ex = traceback.format_exc()
        print(error_ex)
        return "Signature verification failed. Possible fraudulent payment.", 400

    except Exception as e:
        print(f"Error: {e}")
        connection_pool.putconn(conn)
        error_ex = traceback.format_exc()
        print(error_ex)
        return "Error In Transactions", 500


@app.route('/profile')
def profile():
    if 'id' in session:
        # Fetch user details
        user = User.query.get(session['id'])
        if user:
            return render_template('profile.html', user=user)
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        new_password = form.password.data

        bool_val = forget_password_send_otp_code(mail, email, new_password)
        if bool_val:
            flash('An OTP has been sent to your email.', 'info')
            return redirect(url_for('verify_otp'))
        else:
            flash('No account found with that email address.', 'danger')  # Only flash when email is not found

    return render_template('forgot_password.html', form=form)  # No need to flash on form failure here


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'id' in session:
        form = OTPVerificationForm()
        if form.validate_on_submit():
            if 'id' in session:
                entered_otp = form.otp.data
                new_password = session.get('new_password')
                email = session.get('email')
                stored_otp = session.get('stored_otp')

                # Pass the result from verify_otp_code_ to be handled here
                return verify_otp_code_(stored_otp, entered_otp, new_password, email)
    else:
        return redirect(url_for('forgot_password'))

    return render_template('verify_otp.html', form=form)


@app.route("/admin_register", methods=['GET', 'POST'])
def admin_register():
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        # Encrypt password
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')

        # password is encrypted and store in db
        key = Encry_Key.query.filter_by(key_type='password').first()
        ency_password = encrypt_message(key.key, form.password.data)

        # Temporarily store user data in session for the registration payment
        user_data= {
            'username': form.username.data,
            'email': form.email.data,
            'phone_number': form.phone_number.data,
            'password': hashed_password,
            'encryption_password': ency_password,
            'town': form.town.data,
            'city': form.city.data
        }

        # Redirect to the payment confirmation page
        # return redirect(
        #     url_for('registration_fee', user_name=form.username.data,
        #             email=form.email.data,
        #             phone_number=form.phone_number.data))

        # Fetch user from the database
        user = Admin.query.filter_by(email=user_data['email']).first()
        if not user:
            save_user_credintial_registerform(connection_pool, user_data,
                                              'admin')
        else:
            return flash("Credentials Already Present, Please Login")

        flash("Admin Registration Successful", "success")
        return redirect(
            url_for("admin_login")
        )

    return render_template('admin_register.html', form=form)



@app.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password,form.password.data):
            # Create a response object
            response = make_response(redirect(url_for('admin_dashboard')))

            # Set the cookie with an expiration time of 1 week (in seconds)
            response.set_cookie('user_id', f'{user.id}',
                                max_age=7 * 24 * 60 * 60)

            return response
        else:
            flash('Admin Login Unsuccessful. Please check email and password',
                  'danger')

    return render_template('admin_login.html', form=form)


@app.route('/admin_add_course', methods=['GET', 'POST'])
def admin_add_course():
    form = CoursePage()
    image_url = None  # Initialize image_url

    if form.validate_on_submit():
        # Extract data from the form
        title = form.title.data
        image_name = form.image_name.data
        course_category = form.course_category.data

        # Connect to Backblaze
        b2_api = connect_to_backblaze()
        bucket_name = 'course-images-dashboard'
        bucket = b2_api.get_bucket_by_name(bucket_name)

        # Handle file upload
        file = form.image.data
        if file:
            try:
                # Secure the filename
                filename = secure_filename(file.filename)

                # Upload directly to Backblaze without saving locally
                file_data = file.read()  # Read file data from the form
                bucket.upload_bytes(file_data, f'course_images/{filename}')

                # Construct the image URL
                # image_url = f"https://f002.backblazeb2.com/file/{bucket_name}/{filename}"
                image_url = filename

            except Exception as e:
                logging.error(f"Error uploading to Backblaze: {e}")
                flash("There was an error uploading the image.", "error")
                return render_template('admin_templates/admin_course_page.html', form=form)

        curriculum_data = {
            "title": title,
            "course_category": course_category,
            "image_url": image_url
        }
        # insert dashboard courses
        insert_dashboard_course(connection_pool, curriculum_data,'course')

        flash("Course added successfully!", "success")
        return redirect(url_for('admin_add_course'))  # Redirect after successful submission

    # If GET request or form validation fails, render the template
    return render_template('admin_course_page.html', form=form)


def upload_videos_image_backblaze(file_to_upload, bucket_name, file_name_image_videos, filename):
    b2_api = connect_to_backblaze()
    bucket = b2_api.get_bucket_by_name(bucket_name)

    # Secure the filename
    filename = secure_filename(filename)

    # Upload directly to Backblaze without saving locally
    file_data = file_to_upload.read()  # Read file data from the form
    bucket.upload_bytes(file_data, f'{file_name_image_videos}/{filename}')


@app.route('/admin_add_enroll_course', methods=['GET', 'POST'])
def admin_add_enroll_course():
    form = CurriculumForm()
    if form.validate_on_submit():
        # Extract form data
        course_name = form.course_name.data
        overview = form.overview.data
        price = form.price.data
        level = form.level.data
        duration = form.duration.data
        lessons = form.lessons.data
        quizzes = form.quizzes.data
        certifications = form.certifications.data

        # For the demo video and banner image, check and upload directly to Backblaze
        if form.demo_video.data:
            demo_video_stream = form.demo_video.data.stream
            demo_video_filename = form.demo_video.data.filename
            upload_videos_image_backblaze(demo_video_stream, 'demo-videos-enroll-course', 'demo_videos', demo_video_filename)

        if form.banner_image.data:
            banner_image_stream = form.banner_image.data.stream
            banner_image_filename = form.banner_image.data.filename
            upload_videos_image_backblaze(banner_image_stream, 'course-images-dashboard', 'banner_images', banner_image_filename)

        curriculum_data = {
            "course_name": course_name,
            "overview": overview,
            "price": price,
            "level": level,
            "duration": duration,
            "lessons": lessons,
            "quizzes": quizzes,
            "certifications": certifications,
            "demo_video": demo_video_filename if form.demo_video.data else None,
            "banner_image": banner_image_filename if form.banner_image.data else None,
            "curriculum": None
        }

        # Capture all weeks and topics
        weeks = []
        for week in form.weeks:
            week_data = {
                "week": week.week.data,
                "title": week.title.data,
                "topics": [topic_form.topic.data for topic_form in week.topics]
            }
            weeks.append(week_data)

        curriculum_data['curriculum'] = {'weeks': weeks}
        insert_course(connection_pool, curriculum_data, 'course_curriculum')
        flash("Data is successfully saved")
    else:
        print(form.errors)

    return render_template('admin_course_curriculum.html', form=form)


@app.route('/admin_enroll_course/<course_name>')
def admin_enroll_course_page(course_name):
    # reading the stored cookie
    user_id = request.cookies.get('user_id')
    if user_id is not None:
        # registration login
        bool_val_registration_cond = regristration_conditions_db(
            connection_pool,
            'registration_payment',
            'registration_transactions',
            user_id)
        if bool_val_registration_cond == False:
            flash(
                'Registration is expired, please register again and purchase courses.')
            return redirect(url_for('register'))

        data = get_curriculum(course_name)
        b2_api = connect_to_backblaze()
        # image_file_name = 'course_images/ai.jpg'
        demo_video_bucket_name = 'demo-videos-enroll-course'
        banner_images_bucket_name = 'course-images-dashboard'

        if data is None:
            return "Course not found or error retrieving course details.", 404

        curriculum_weeks = data.get('curriculum', {}).get('weeks', [])
        for week in curriculum_weeks:
            topics = week['topics'][0].split(',')
            week['topics'] = topics

        print(curriculum_weeks)

        overview = data.get('overview')
        price = data.get('price')
        level = data.get('level')
        duration = data.get('duration')
        lessons = data.get('lessons')
        quizzes = data.get('quizzes')
        certifications = data.get('certifications')
        demo_video = get_file_url(b2_api, demo_video_bucket_name, f'demo_videos/{data.get('demo_video')}')
        # banner_image = data.get('banner_image')
        banner_image = get_file_url(b2_api, banner_images_bucket_name, f'banner_images/{data.get('banner_image')}')
        print(demo_video,banner_image)

        return render_template('enroll.html', curriculum=curriculum_weeks,
                               overviews=overview,
                               course_name=course_name, price=price,
                               level=level, duration=duration, lessons=lessons,
                               quizzes=quizzes,
                               certifications=certifications, demo_video=demo_video, banner_image=banner_image)
    flash('Session has expired, please login again.')
    return redirect(url_for('login'))




@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/enroll')
def enroll():
    return render_template('enroll.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('id', None)
    response = make_response(redirect(url_for('home')))
    response.set_cookie('user_id', '', expires=0)
    flash('You have been logged out.', 'info')
    return response

@app.route('/forgot')
def forgot():
    print("dfs")

if __name__ == '__main__':
    app.run(debug=True)
