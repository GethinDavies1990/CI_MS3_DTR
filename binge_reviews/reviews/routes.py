from flask import (Flask, flash,
                   render_template, redirect,
                   request, session, url_for, Blueprint)
from bson.objectid import ObjectId
from binge_reviews import mongo


# Create a reviews object as a blueprint
reviews = Blueprint('reviews', __name__)


@reviews.route("/")
@reviews.route("/get_reviews")
def get_reviews():
    """
    This function will display all the reviews posted 
    by users.
    """
    reviews = list(mongo.db.reviews.find())
    return render_template("reviews.html", reviews=reviews)


@reviews.route("/search", methods=["GET", "POST"])
def search():
    """
    This function allows the user to search for reviews by
    film name and by review description.
    """
    query = request.form.get("query")
    reviews = list(mongo.db.reviews.find({"$text": {"$search": query}}))
    return render_template("reviews.html", reviews=reviews)


@reviews.route("/add_review", methods=["GET", "POST"])
def add_review():
    """
    This function allows the user to add reviews to the
    application. On succesfull submission the user is 
    redirected to the reviews.html page.
    """
    if request.method == "POST":
        review = {
            "film_name": request.form.get("film_name"),
            "review_title": request.form.get("review_title"),
            "category_name": request.form.get("category_name"),
            "review_description": request.form.get("review_description"),
            "created_by": session["user"]
        }
        mongo.db.reviews.insert_one(review)
        flash("Review Published")
        return redirect(url_for('reviews.get_reviews'))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_review.html", categories=categories)


@reviews.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    """
    This fucntion allows the user to edit their own
    review, the user must be in session and can only edit their
    own reviews.
    """
    if request.method == "POST":
        submit = {"$set": {
            "film_name": request.form.get("film_name"),
            "review_title": request.form.get("review_title"),
            "category_name": request.form.get("category_name"),
            "review_description": request.form.get("review_description"),
            "created_by": session["user"]
        }}
        mongo.db.reviews.update_one({"_id": ObjectId(review_id)}, submit)
        flash("Review Successfully Edited")

    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "edit_review.html", review=review, categories=categories)


@reviews.route("/delete_review/<review_id>")
def delete_review(review_id):
    """
    This function allows the user to delete their own reviews.
    they will not be able to delete other user reviews. 
    """
    mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
    flash("Review Successfully Removed")
    return redirect(url_for('reviews.get_reviews'))