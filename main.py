from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login",methods=['GET','POST'])
def login():
    return render_template("login.html")

@app.route("/logout",methods=['GET','POST'])
def logout():
    return render_template("logout.html")

@app.route("/about",methods=['GET','POST'])
def about():
    return render_template("about.html")

@app.route("/contact",methods=['GET','POST'])
def contact():
    return render_template("contact.html")

@app.route("/profile",methods=['GET','POST'])
def profile():
    return render_template("profile.html")





if __name__ == "__main__":
    app.run(debug=True)