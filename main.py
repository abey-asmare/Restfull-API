from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from random import choice
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
legal_api_key = "abeyasmare1234"

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random")
def random():
    all_cafes = Cafe.query.all()
    random_cafe = choice(all_cafes)
    return jsonify( cafe = random_cafe.to_dict())

@app.route("/all")
def all():
    all_cafes = Cafe.query.all()
    cafes = [ cafe.to_dict() for cafe in all_cafes]
    return jsonify(cafes = cafes)

@app.route("/search")
def get_cafe():
    cafe = Cafe.query.filter_by(location = request.args.get('loc').title()).first()
    if cafe:
        return jsonify(cafe = cafe.to_dict())
    return jsonify(error = {"Not found":  "Sorry, we don't have a cafe at that location."})

## HTTP POST - Create Record
@app.route("/add", methods = ["POST", "GET"])
def add():
    if request.method == "POST":
        if request.form.get("can_take_calls") == "true":
            can_take_calls = True
        else:
            can_take_calls = False

        if request.form.get("has_toilet")== "true":
            has_toilet = True
        else:
            has_toilet = False

        if request.form.get("has_wifi") == "true":
            has_wifi = True
        else:
            has_wifi = False

        if request.form.get("has_sockets") == "true":
            has_sockets = True
        else:
            has_sockets = False
        print(request.form.get("location"))

        new_cafe = Cafe(
            name = request.form.get("name"),
            location = request.form.get("location"),
            seats = request.form.get("seats"),
            map_url = request.form.get("map_url"),
            img_url = request.form.get("img_url"),
            coffee_price = request.form.get("coffee_price"),
            has_sockets = has_sockets,
            has_wifi = has_wifi,
            can_take_calls = can_take_calls,
            has_toilet = has_toilet,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response = {"success": "successfully added the new cafe"})
    return redirect(url_for("home"))

## HTTP PUT/PATCH - Update Record
id = 22
@app.route("/update-price/<int:id>", methods = ["PATCH"])
def update_price(id):
    cafe = Cafe.query.get(id)
    if cafe:
        cafe.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify(success = "successfully updated the price")
    return jsonify(error = "cafe doesnt exist")



## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods = ["DELETE"])
def delete_closed(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    api_key = request.args.get("api_key")

    if cafe:
        if  api_key == legal_api_key:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(successful = "deleted successfully")
        return jsonify(error = "unauthorized")
    return jsonify(error = "cafe doesnot exist")

if __name__ == '__main__':
    app.run(debug=True)
