import os
from flask import (Flask , flash , render_template , redirect , request , session , url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash , check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipe.html" , recipes=recipes)


@app.route("/register" , methods = ["GET" , "POST"])
def register():
    if request.method == "POST":
# check if username already in Database
        existing_user = mongo.db.users.find_one(
            {"username" : request.form.get("username").lower()})
# 
        if existing_user:
            flash("Username alredy exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)
# put new user into 'session' cookie
        session["users"] = request.form.get("username").lower()
        flash("Registration Successful")
    return render_template("register.html")


@app.route("/login" , methods=["GET" , "POST"])
def login():
    if request.method == "POST":
#existing user in dadabase
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
# checks if password matches user 

            if check_password_hash(existing_user["password"] , request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome back , {}".format(request.form.get("username")))
            else:
# wrong password
                flash("Wrong Username and/or Password")
                return redirect(url_for("login"))

        else:
# username don't exist in database
            flash("Wrong Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

if __name__== "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
#Delete that to False befor submission
            debug=True)