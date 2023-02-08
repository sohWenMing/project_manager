from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
from forms.forms import LoginForm, CreateUserForm, CreateSkillForm, DeleteSkillForm, DeleteUserForm, AddSkillForm, CreateProjectForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

def get_entered_skills():
        skills_data = {}
        skills_dict = {}
        entered_skills = []
        skill_result = Skill.query.all()
        for skill in skill_result:
            entered_skills.append(skill.skill)
            skills_dict[skill.skill] = skill.id
        entered_skills=sorted(entered_skills)
        skills_data['skills_dict'] = skills_dict
        skills_data['entered_skills'] = entered_skills
        return skills_data

def get_user_data():
    user_data = {}
    user_names_dict = {}
    user_result = User.query.all()
    for user in user_result:
        user_names_dict[user.first_name + ' ' + user.last_name] = user.staff_id
    name_list = []
    for key, value in user_names_dict.items():
        name_list.append(key)
    name_list = sorted(name_list)
    user_data['user_dict'] = user_names_dict
    user_data['name_list'] = name_list
    return user_data

def get_management_data():
    management_data = {}
    management_names_dict = {}
    management_result = User.query.filter((User.admin_level=='manager') | (User.admin_level=='admin')).all()
    for manager in management_result:
        management_names_dict[manager.first_name + ' ' + manager.last_name] = manager.staff_id
    name_list = []
    for key, value in management_names_dict.items():
        name_list.append(key)
    name_list=sorted(name_list)
    management_data['user_dict'] = management_names_dict
    management_data['name_list'] = name_list
    return management_data


app.config.from_object(Config)
db = SQLAlchemy()
db.init_app(app)

user_skills = db.Table('user_skills',
db.Column('id', db.Integer, primary_key=True),
db.Column('user_id', db.Integer, db.ForeignKey('users.staff_id')),
db.Column('skills_id', db.Integer, db.ForeignKey('skills.id'))
)

class User(db.Model):
    __tablename__ = 'users'
    staff_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    admin_level = db.Column(db.String, nullable=False)
    hourly_rate = db.Column(db.Integer, nullable=False)
    skill_list = db.relationship('Skill', secondary=user_skills, backref='skilled_personnel')
    projects_managed = db.relationship('Project', backref='manager')
    billed_hours = db.relationship('Billing', backref='hours_billed')
    def __repr__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String, unique=True, nullable=False)
    def __repr__(self) :
        return '<Skill {}>'.format(self.skill)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    project_name  = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Integer, nullable=False)
    end_date = db.Column(db.Integer, nullable=False)
    project_manager = db.Column(db.Integer, db.ForeignKey('users.staff_id'))
    def __repr__(self):
        return '<Project {}>'.format(self.project_name)

class Billing(db.Model):
    __tablename__ = 'billings'
    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.Integer, db.ForeignKey('projects.id'))
    staff = db.Column(db.Integer, db.ForeignKey('users.staff_id'))
    projected = db.Column(db.Integer, nullable = False)
    billed = db.Column(db.Integer, nullable = False)
    date = db.Column(db.Integer, nullable=False)
    no_hours = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

### routes ###
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='index')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {} | remember_me={}'.format(form.user.data, form.remember_me.data))
        return redirect(url_for('index'))
    
    return render_template('login.html', title="Sign In", form=form)

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        first_name = form.first_name.data.strip().capitalize()
        last_name = form.last_name.data.strip().capitalize()
        username = form.user.data
        password_hash = generate_password_hash(form.password.data, method='sha256')
        email = form.email.data
        admin_level = form.admin_classification.data
        hourly_rate = form.hourly_rate.data
        username_check = User.query.filter_by(username=username).all()
        email_check = User.query.filter_by(email=email).all()
        if username_check != [] or email_check != []:
            return redirect(url_for('create_user', error_message='Username or Email has been previously used'))
        else:
            user = User(
                first_name = first_name,
                last_name = last_name,
                username = username,
                password_hash = password_hash,
                email = email,
                admin_level = admin_level,
                hourly_rate = hourly_rate
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('create_user', username=username))
            
    return render_template('create_user.html', title="Create New User", form=form)

@app.route('/delete_user', methods = ["GET", "POST"])
def delete_user():
    user_data = get_user_data()
    name_list = user_data['name_list']
    form = DeleteUserForm()
    form.delete_user.choices = [(entry, entry) for entry in name_list]

    if request.method == 'POST':
        index_to_delete = user_data['user_dict'][form.delete_user.data]
        queried_user = User.query.filter_by(id=index_to_delete).first()
        db.session.delete(queried_user)
        db.session.commit()
        return redirect(url_for('delete_user', user_deleted=form.delete_user.data))
    return render_template('delete_user.html', form=form)

@app.route('/manage_skill', methods=['GET', 'POST'])
def manage_skill():
    user_data = get_user_data()
    skills_data = get_entered_skills()
    entered_skills = skills_data['entered_skills'] 
    name_list = user_data['name_list']
    form = AddSkillForm()
    form.users.choices = [(entry, entry) for entry in name_list]
    form.skills.choices = [(entry, entry)for entry in entered_skills]

    if form.validate_on_submit():
        print(user_data['user_dict'])
        user = User.query.filter_by(staff_id=user_data['user_dict'][form.users.data]).one()
        skill = Skill.query.filter_by(id=skills_data['skills_dict'][form.skills.data]).one()
        if skill not in user.skill_list:
            print(user, skill)
            user.skill_list.append(skill)
            db.session.commit()
            return redirect(url_for('manage_skill', success='Skill successfully added'))
        else:
            return redirect(url_for('manage_skill', user=form.users.data, skill=form.skills.data))
    
    return render_template('manage_skill.html', form=form)

@app.route('/create_skill', methods=["GET", "POST"])
def create_skill():
    skills_data = get_entered_skills()
    entered_skills = skills_data['entered_skills']

    #inital query to pull all entered skills from database
   
# form for entry of new skill  
    form = CreateSkillForm()
    if form.validate_on_submit():
        final_skill_string = ""
        cleaned_list = []
        entered_skill_word_list = form.skill.data.strip().lower().split()
        for word in entered_skill_word_list:
            cleaned_list.append(word.capitalize())

        if len(entered_skill_word_list) != 1:
            for i in range(0, len(cleaned_list) - 1):
                final_skill_string = final_skill_string + cleaned_list[i] + " "
            final_skill_string = final_skill_string + cleaned_list[len(cleaned_list) - 1]
        else:
            final_skill_string = cleaned_list[0]

        skill = Skill(
            skill = final_skill_string
        )
        if final_skill_string not in entered_skills:
            db.session.add(skill)
            db.session.commit()
            return redirect(url_for('create_skill', skill_created = final_skill_string))
        else:
            return redirect(url_for('create_skill', error_message = 'Skill Previously Entered'))

    return render_template('create_skill.html', title='Manage Skill Classification', form=form, entered_skills = entered_skills)

#form for deletion of skill
@app.route('/delete_skill', methods=['GET', 'POST'])
def delete_skill():

    skills_data = get_entered_skills()
    entered_skills = skills_data['entered_skills']
    
    form = DeleteSkillForm()
    form.delete_skill.choices = [(entry, entry) for entry in entered_skills]

    if form.validate_on_submit():
        print(form.delete_skill.data, type(form.delete_skill.data))
        skill = form.delete_skill.data
        queried_skill = Skill.query.filter_by(skill=skill).first()
        print(skill)
        db.session.delete(queried_skill)
        db.session.commit()
        return redirect(url_for('delete_skill'))

        
    return render_template('delete_skill.html', form = form, entered_skills=entered_skills)

@app.route('/create_project', methods=['GET','POST'])
def create_project():

    management_data = get_management_data()
    managers = management_data['name_list']

    project_name_list = []
    project_query = Project.query.all()
    for project in project_query:
        project_name_list.append(project.project_name)
    print(project_name_list)
    
    form = CreateProjectForm()
    form.project_manager.choices = [(entry, entry) for entry in managers]

    if request.method == "POST":
        start_date = form.start_date.data
        start_date_dt = datetime(start_date.year, start_date.month, start_date.day)
        start_date_timestamp = datetime.timestamp(start_date_dt)
        
        end_date = form.end_date.data
        end_date_dt = datetime(end_date.year, end_date.month, end_date.day)
        end_date_timestamp = datetime.timestamp(end_date_dt)
        
        if form.project_name.data in project_name_list:
            return redirect(url_for('create_project', error = "Project Name Taken"))
       
        elif end_date_timestamp < start_date_timestamp:
            return redirect(url_for('create_project', error='End date is earlier or on start date'))

        else: 
            manager_id = management_data['user_dict'][form.project_manager.data]
            manager = User.query.filter_by(staff_id=manager_id).one()
            project = Project (
                project_name = form.project_name.data,
                budget = form.budget.data,
                start_date = start_date_timestamp,
                end_date = end_date_timestamp
            )
            db.session.add(project)
            db.session.commit()
            project_to_add = Project.query.filter_by(project_name=form.project_name.data).one()
            manager.projects_managed.append(project_to_add)
            db.session.commit()
            return redirect(url_for('create_project', success="Project {} Successfully Added".format(form.project_name.data)))



        
    
    
    return render_template('create_project.html', form=form)
        

if __name__ == ('__main__'):
    app.run(debug=True)
