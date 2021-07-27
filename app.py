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
def home():
    return render_template("home.html"  )


@app.route("/register" , methods = ["GET" , "POST"])
def register():
    if request.method == "POST":
# check if username already in Database
        existing_user = mongo.db.users.find_one(
            {"username" : request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)
# put new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile" , username = session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                flash("Wrong Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Wrong Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" in session:
        return render_template("profile.html", username = session["user"])

    return redirect(url_for("login"))


@app.route("/search" , methods = ["GET" , "POST" ])
def search():
    search = request.form.get("search")
    recipes = list(mongo.db.recipes.find({"$text" : {"$search" : search}}))
    return render_template("recipe.html" , recipes=recipes)

@app.route("/logout")
def logout():
    
    flash("The user has logged out")
    session.clear()
    return redirect(url_for("login"))


@app.route("/categories/<selected_category>")
def categories(selected_category):
    recipes = mongo.db.recipes.find()
    return render_template("categories.html" , recipes = recipes , selected_category = selected_category , page_title=selected_category + "Recipes")


@app.route("/recipe/<recipe_id>")
def recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe.html" , recipe=recipe , page_title = "See Recipe")

@app.route("/add_recipe")
def add_recipe():
    categories = mongo.db.categories.find()
    return render_template("add_recipe.html" , categories=categories , page_title= "Add your Recipe" )


@app.route("/insert_recipe" , methods = ["POST"])
def insert_recipe():
    recipes = mongo.db.recipes
    form_data = request.form.to_dict()
    ingrediants_list = form_data["recipe_ingredients"].split("\n")
    method_list = form_data["recipe_method"].split("\n")
    recipe =  recipes.insert_one(
        {
        "category_name": form_data["category_name"],
        "recipe_name": form_data["recipe_name"],
        "recipe_img": form_data["recipe_img"],
        "recipe_method" : method_list,
        "recipe_ingredients": ingrediants_list
        }
    )
    flash("Your recipe has been added")
    return redirect(url_for("recipe", recipe_id=recipe.inserted_id))


@app.route("/edit_recipe/<recipe_id>")
def edit_recipe(recipe_id):
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find()
    ingrediants_list = [ingredient for ingredient in the_recipe['recipe_ingredients']]
    method_list = [method for method in the_recipe['recipe_method']]

    ingredient_text = "\n".join(ingrediants_list)
    method_text = "\n".join(method_list)

    return render_template("edit_recipe.html" , recipe= the_recipe , categories=categories , ingredient = ingredient_text ,
                     method = method_list , page_title="Edit Recipe")


@app.route("/update_recipe/<recipe_id>" , methods = ["POST"])
def update_recipe(recipe_id):
    recipe = mongo.db.recipes
    form_data - request.form.to_dict()
    ingrediants_list = form_data["recipe_ingredients"].split("\n" )
    method_list = form_data["recipe_method"].split("\n")
    recipe.update({"_id": ObjectId(recipe_id)}),
    {
            "category_name": form_data["category_name"],
            "recipe_name": form_data["recipe_name"],
            "recipe_img": form_data["recipe_img"],
            "recipe_method" : method_list,
            "recipe_ingredients": ingrediants_list
        }


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Successfully Deleted")
    return redirect(url_for("home"))



if __name__== "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)