from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm, EventForm
from models import Event, User, db

app = Flask(__name__)
##We need a secret key
app.config["SECRET_KEY"] = "create_a_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('week_view'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
@app.route('/week', methods=['GET', 'POST'])
@login_required
def week_view():
    # Retrieve events for the current week for the logged-in user
    events = Event.query.filter_by(user_id=current_user.id).all()  # Adjust date logic
    return render_template('week_view.html', events=events)


@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            name=form.name.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added!', 'success')
        return redirect(url_for('week_view'))
    return render_template('add_event.html', form=form)


@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.name = form.name.data
        event.date = form.date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.description = form.description.data
        db.session.commit()
        flash('Event updated!', 'success')
        return redirect(url_for('week_view'))
    return render_template('edit_event.html', form=form, event=event)


@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted!', 'success')
    return redirect(url_for('week_view'))


if __name__ == '__main__':
    app.run(debug=True)




