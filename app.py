from flask import Flask, render_template, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import User, db, connect_db, Feedback
from forms import UserForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///demo_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def register():
    """Show a form that when submitted will register/create a user. 
    This form should accept a username, password, email, first_name, and last_name. 
    Make sure you are using WTForms and 
    that your password input hides the characters that the user is typing!"""
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        user = User.register(username, password, email, firstname, lastname)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append(
                'Username taken, Please use another username')
            return render_template('register.html', form=form)
        session['user_name'] = user.username
        flash("Welcome Sucessfully Created Your Account", "Success")
        return redirect(f'/users/{user.username}')

    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Show a form that when submitted will login a user. 
    This form should accept a username and a password. 
    Make sure you are using WTForms and that your password input hides 
    the characters that the user is typing!
    POST /login : Process the login form, ensuring the user is authenticated and going to /secret if so.

    """
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}!", "primary")
            session['user_name'] = user.username
            session['admin'] = user.is_admin
            print(session['user_name'])
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors.append('Wrong username/password, try again')
    return render_template('login.html', form=form)


@app.route("/users/<string:username>")
def detail(username):
    if 'user_name' not in session:
        flash("Please login first!", "danger")
        return render_template('404.html'), 404
    u = User.query.filter_by(username=username).first()
    if session['admin'] and session['user_name'] == u.username:
        feedbacks = Feedback.query.all()
        return render_template('details.html', user=u, feedbacks=feedbacks)
    elif u and session['user_name'] == u.username:
        feedbacks = Feedback.query.filter_by(username=u.username).all()
        return render_template('details.html', user=u, feedbacks=feedbacks)
    else:
        return render_template('401.html'), 401


@app.route("/users/<string:username>/delete", methods=["POST"])
def delete_user(username):
    """Remove the user from the database and make sure to also delete all of their feedback."""
    if 'user_name' not in session:
        flash("Please login first!", "danger")
        return render_template('401.html'), 401

    logged_in_user = User.query.filter_by(
        username=session['user_name']).first()
    # Check if the logged-in user is not found
    if not logged_in_user:
        flash("You don't have permission to do that!", "danger")
        return render_template('401.html'), 401

    user_to_delete = User.query.filter_by(username=username).first()

    if user_to_delete:
        # Delete all feedback associated with the user
        Feedback.query.filter_by(username=username).delete()
        # Delete the user
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User and their feedback deleted", "info")
        return redirect('/')
    else:
        flash("User not found", "danger")
        return render_template('404.html'), 404


@app.route('/users/<string:username>/feedback/add', methods=["GET", "POST"])
def feedback_form(username):
    form = FeedbackForm()
    if 'user_name' in session:
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            feedback = Feedback(
                title=title, content=content, username=username)
            if feedback:
                db.session.add(feedback)
                db.session.commit()
            else:
                form.title.errors.append("please fill out all")
            return redirect(f'/users/{username}')
    else:
        return render_template('401.html'), 401
    return render_template('feedback.html', form=form)


@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def update_feedback(id):
    old_feedback = Feedback.query.get_or_404(id)

    if 'user_name' in session:
        if old_feedback.validate_on_submit():
            old_feedback.title = old_feedback.title.data
            old_feedback.content = old_feedback.content.data
            db.session.commit()
            return redirect(f'/users/{old_feedback.username}')
    return render_template('edit_feedback.html', form=old_feedback)


@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_feedback(id):
    if 'user_name' not in session:
        flash("Please login first", "danger")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(id)
    if feedback.username == session['user_name'] or session['admin']:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted", "info")
        return redirect(f"/users/{session['user_name']}")
    flash("You don't have permission to do that!", "danger")
    return redirect(f"/users/{session['user_name']}")

# @app.route('/secret')
# def secret():
#     if 'user_name' not in session:
#         flash("Please login first", "danger")
#         return redirect('/login')
#     flash("This is the secret")
#     return render_template('secret.html')


@app.route('/logout')
def logout_user():

    session.pop('user_name')
    flash("Goodbye!", "info")
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', 404)


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html', 401)
