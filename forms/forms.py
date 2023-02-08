from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, EmailField, SelectField, RadioField, DateField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo

class LoginForm(FlaskForm):
    user = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateUserForm(FlaskForm):
    first_name = StringField('Input First Name :', validators=[DataRequired()])
    last_name = StringField('Input Last Name :', validators=[DataRequired()])
    user = StringField('Input Username :', validators=[DataRequired()])
    password = PasswordField('Input Password :', validators=[DataRequired(message="Input Required"), EqualTo('confirm')])
    confirm = PasswordField('Confirm Password :', validators = [DataRequired()])
    email = EmailField('Email :', validators=[DataRequired(), Email()])
    admin_classification = RadioField('Admin Level :', choices = [
    ('admin', 'Master Administrator'),
    ('manager', 'Manager'),
    ('staff', 'Staff')
    ], validators=[DataRequired()])
    hourly_rate = IntegerField('Enter Hourly Rate(Integer Value)', validators=[DataRequired(), NumberRange(min=10, max=200)])
    submit = SubmitField('Create New User')

class CreateSkillForm(FlaskForm):
    skill = StringField('Enter Skill Classification :', validators=[DataRequired()])
    submit = SubmitField('Create New Skill Classification')

class DeleteSkillForm(FlaskForm):
    delete_skill = SelectField('Select Skill to Delete :')
    submit = SubmitField('Delete Skill')

class DeleteUserForm(FlaskForm):
    delete_user = SelectField('Select User to Delete :')
    submit = SubmitField('Delete User')

class AddSkillForm(FlaskForm):
    users = SelectField('Select User')
    skills = SelectField('Select Skill')
    submit = SubmitField('Add Skill')

class CreateProjectForm(FlaskForm):
    project_name = StringField('Enter Project Name :', validators=[DataRequired()])
    budget = IntegerField('Enter Budget :', validators=[DataRequired()])
    start_date = DateField('Enter Start Date', validators=[DataRequired()])
    end_date = DateField('Enter End Date', validators=[DataRequired()])
    project_manager = SelectField('Select Project Manager')
    submit = SubmitField('Create Project')


    
