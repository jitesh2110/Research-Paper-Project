from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_from_directory,
)
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)
from forms import RegisterForm, LoginForm, PostForm
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

import os

app = Flask(__name__)
Bootstrap(app)

# Configurations
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    r"sqlite:///D:\Shreyas\python tutorials\project_work\users.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = (
    r"D:\\Shreyas\\python tutorials\\project_work\\static\\documents"
)
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User model
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    posts = db.relationship("Post", back_populates="author")


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", back_populates="posts")
    collaborators = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    department = db.Column(db.String(250), nullable=False)
    categories = db.Column(db.String(250), nullable=False)
    document = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


# Routes
@app.route("/")
def home():
    all_posts = Post.query.all()

    return render_template("index.html", all_posts=all_posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for("login"))

        login_user(user)

        return redirect(url_for("profile"))

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data

        password = form.password.data
        name = form.name.data

        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please log in.", "error")
            return redirect(url_for("login"))

        new_user = User(
            email=email,
            password=generate_password_hash(
                password, method="pbkdf2:sha256", salt_length=8
            ),
            name=name,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Registration successful!", "success")
        return redirect(url_for("profile"))
    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error[0]}", "error")

    return render_template("register.html", form=form)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("index.html")


@app.route("/paper/<int:paper_id>", methods=["GET", "POST"])
def paper(paper_id):
    paper = Post.query.get_or_404(paper_id)
    return render_template("paper.html", paper=paper)


@app.route("/makepaper", methods=["GET", "POST"])
@login_required
def makepaper():
    form = PostForm()
    if form.validate_on_submit():
        collaborators = form.collab_authors.data
        title = form.title.data
        body = form.body.data
        department = form.department.data
        categories = form.categories.data
        document = request.files.get("document")
        if not document:
            flash("No document uploaded. Please upload a document.", "error")
            return redirect(url_for("makepaper"))
        filename = document.filename
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        document.save(filepath)

        new_post = Post(
            title=title,
            body=body,
            author=current_user,
            collaborators=collaborators,
            department=department,
            categories=categories,
            document=filepath,
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for("profile"))

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error[0]}", "error")

    return render_template("make_post.html", form=form)


@app.route("/download/<path:filepath>")
def download(filepath):
    filename = os.path.basename(filepath)
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename, as_attachment=True
    )


@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author == current_user:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully!", "success")
    else:
        flash("You do not have permission to delete this post.", "error")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
