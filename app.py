from flask import Flask, render_template, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///feedback_app"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "supersecret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.errorhandler(Unauthorized)
def handle_unauthorized_error(error):
    """Handle Unauthorized exceptions and return a 401 status code."""
    return render_template("errors/401.html"), 401


@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors and return custom 404 page."""
    return render_template("errors/404.html"), 404


@app.route('/')
def home_page():
    """Redirects to register page"""
    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Render registration form and adds new user to database."""
    if "username" in session:
      return redirect(f"/users/{session['username']}")
    
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username=username,
                                 password=password, 
                                 email=email, 
                                 first_name=first_name,
                                 last_name=last_name)

        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another.')
            return render_template("users/register.html", form=form)
        
        session['username'] = new_user.username

        return redirect(f"/users/{new_user.username}")
    else:
        return render_template("users/register.html", form=form)
    

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Renders login form and sends info to update session."""
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password.']
            return render_template("users/login.html", form=form)
        
    return render_template("users/login.html", form=form)


@app.route('/users/<username>')
def show_user_details(username):
    """Renders user information"""
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    return render_template("users/details.html", user=user)


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Deletes user and all of their feedback from database"""
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get_or_404(username)
    
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def feedback_form(username):
    """Displays and Submits Feedback Form"""
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_feedback = Feedback(title=title,
                                content=content,
                                username=username)

        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f"/users/{new_feedback.username}")
    else:
      return render_template("feedback/add.html", form=form)
    

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def edit_feedback(feedback_id):
    """Renders form to edit individual feedback & makes changes."""
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    return render_template("/feedback/edit.html", feedback=feedback, form=form)


@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Deletes a specific pience of feedback and redirects to user profile."""
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    db.session.delete(feedback)
    db.session.commit()

    return redirect(f"/users/{feedback.username}")


@app.route('/logout')
def logout_user():
    """Logs user out"""
    if "username" not in session:
      return redirect('/')
    else:
      session.pop('username')
      return redirect('/')
