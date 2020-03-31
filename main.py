from flask import Flask, render_template, redirect, request
from flask_ngrok import run_with_ngrok
import os
from data import db_session
from data.users import User
from data.requests import Requests
import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.login_form import LoginForm
from data.requests_form import RequestsForm
from flask_restful import abort

app = Flask(__name__)
run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/requests.sqlite")


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Войти')


@app.route("/")
def index():
    session = db_session.create_session()
    if current_user.is_authenticated:
        requests = session.query(Requests).filter(Requests.user == current_user)
    else:
        requests = session.query(Requests).filter(False)
    return render_template("index.html", requests=requests)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/requests', methods=['GET', 'POST'])
@login_required
def add_requests():
    form = RequestsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        requests = Requests()
        requests.title = form.title.data
        requests.about = form.about.data
        requests.classroom = form.classroom.data
        requests.priority = form.priority.data
        current_user.requests.append(requests)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('requests.html', title='Добавление заявки', form=form)


@app.route('/requests/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_requests(id):
    form = RequestsForm()
    if request.method == "GET":
        session = db_session.create_session()
        requests = session.query(Requests).filter(Requests.id == id, Requests.user == current_user).first()
        if requests:
            form.title.data = requests.title
            form.about.data = requests.about
            form.classroom.data = requests.classroom
            form.priority.data = requests.priority
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        requests = session.query(Requests).filter(Requests.id == id, Requests.user == current_user).first()
        if requests:
            requests.title = form.title.data
            requests.about = form.about.data
            requests.classroom = form.classroom.data
            requests.priority = form.priority.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('requests.html', title='Редактирование заказа', form=form)


@app.route('/requests_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def requests_delete(id):
    session = db_session.create_session()
    requests = session.query(Requests).filter(Requests.id == id, Requests.user == current_user).first()
    if requests:
        session.delete(requests)
        session.commit()
    else:
        abort(404)
    return redirect('/')



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)