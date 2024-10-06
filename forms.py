from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, Optional
from models import User, Admin


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Regexp(regex=r'^\d{10}$', message="Phone number must be 10 digits.")])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(max=12, message='Password must be less than 12 characters.'),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{1,12}$',
               message='Password must include at least one special character and one number.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    town = StringField('Town', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    reference_id = StringField('Reference Id')
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        # print(user)
        if user:
            raise ValidationError('The email is already registered. Please use a different one.')

    def validate_phone_number(self, phone_number):
        phone_number_user = User.query.filter_by(phone_number=phone_number.data).first()
        if phone_number_user:
            raise ValidationError('The phone number is already in use. Please provide a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min = 6,max = 12,message='Password must be between 6 and 12 characters long')])
    submit = SubmitField('Login')

class VideoUploadForm(FlaskForm):
    file = FileField('Upload Video', validators=[
        FileRequired(),
        FileAllowed(['mp4', 'avi', 'mov', 'wmv'], 'Videos only!')
    ])
    submit = SubmitField('Upload')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(max=12, message='Password must be less than 12 characters.'),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{1,12}$',
               message='Password must include at least one special character and one number.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Submit')

class OTPVerificationForm(FlaskForm):
    otp = IntegerField('OTP', validators=[DataRequired()])
    submit = SubmitField('Submit')  # Add a submit button


class PaymentForm(FlaskForm):
    coupon = StringField('Coupon Code', validators=[Length(min=2, max=50)])
    submit = SubmitField('Submit')


class CoursePage(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image_name = StringField('Image Name', validators=[DataRequired()])
    course_category = StringField('Course Category', validators=[DataRequired()])
    image = FileField('Course Image', validators=[DataRequired()])
    submit = SubmitField('Submit')


class TopicForm(FlaskForm):
    csrf = False
    topic = StringField('Topic', validators=[DataRequired()])

class WeekForm(FlaskForm):
    csrf = False
    week = StringField('Week', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    topics = FieldList(FormField(TopicForm), min_entries=1)

class CurriculumForm(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])
    overview = StringField('Overview', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    level = StringField('Level', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    lessons = IntegerField('Lessons', validators=[DataRequired()])
    quizzes = IntegerField('Quizzes', validators=[DataRequired()])
    certifications = StringField('Certifications', validators=[DataRequired()])
    demo_video = FileField('Demo Video')
    banner_image = FileField('Banner Image')
    weeks = FieldList(FormField(WeekForm), min_entries=1)
    submit = SubmitField('Submit')


class CourseVideo(FlaskForm):
    course_id = IntegerField('Course ID', validators=[DataRequired()])
    week_number = IntegerField('Week Number', validators=[DataRequired()])
    video_name = StringField('Video Name', validators=[DataRequired()])
    video_number = IntegerField('Video Number', validators=[DataRequired()])
    week_topic = StringField('Week Topic', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Form for each Video
class VideoForm(FlaskForm):
    video = FileField('Upload Video', validators=[Optional()])  # Upload Video





