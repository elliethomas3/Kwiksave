#importing libraries
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

#configuring database
app.secret_key = "123456"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db = SQLAlchemy(app)

#create SQL table to store users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

#creating home page
@app.route('/')
def home():
    #checks if user has valid login session
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    return render_template("home.html", user=user)

#creating registration system
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

#creating the login system
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Find user in SQL database
        user = User.query.filter_by(email=email).first()

        #checks in password entered matches stored password hash
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id

            return redirect("/")

        return "Invalid email or password!"

    return render_template("login.html")

#removes users session/ logs them out
@app.route("/logout")
def logout():

    session.pop("user_id", None)

    return redirect("/login")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)