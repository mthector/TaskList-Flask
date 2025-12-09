from wtforms import Form, SelectField, StringField, DateTimeField, TextAreaField, SubmitField, PasswordField, validators, ValidationError
import datetime

class TaskForm(Form):
    name = StringField('Task Name', [validators.length(min=4, max=80), validators.DataRequired()])
    description = TextAreaField('Description', [validators.Optional()])
    due_date = DateTimeField('Due Date', [validators.Optional()], format='%Y-%m-%dT%H:%M')
    category_id = SelectField('Category', [validators.DataRequired()], choices=[], coerce=int)
    submit = SubmitField('Save Task')

    def validate_due_date(form, field):
        if field.data and field.data < datetime.datetime.now():
            raise ValidationError('Due date cannot be in the past')


class LoginForm(Form):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.length(min=6, message='Password must be at least 6 characters')
    ])
    submit = SubmitField('Sign In')


class RegisterForm(Form):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Account')