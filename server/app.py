#!/usr/bin/env python3


from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

# Setting up the database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initializing and configuring a Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Setting up database migration
migrate = Migrate(app, db)

# Initializing the database with the app
db.init_app(app)

# Setting up Flask-RESTful API
api = Api(app)

class Restaurants(Resource):
    """Resource for handling requests to /restaurants"""
    def get(self):
        """GET request to retrieve all restaurants"""
        restaurants = [{"id": r.id, "name": r.name, "address": r.address} for r in Restaurant.query.all()]
        return make_response(restaurants, 200)

class RestaurantByID(Resource):
    """Resource for handling requests to /restaurants/<id>"""
    def get(self, id):
        """GET request to retrieve a specific restaurant by ID"""
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        response_dict = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "pizza_id": rp.pizza_id,
                    "restaurant_id": rp.restaurant_id,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients
                    }
                } for rp in restaurant.restaurant_pizzas
            ]
        }
        return make_response(response_dict, 200)

    def delete(self, id):
        """DELETE request to remove a specific restaurant by ID"""
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)

class Pizzas(Resource):
    """Resource for handling requests to /pizzas"""
    def get(self):
        """GET request to retrieve all pizzas"""
        pizzas = [{"id": p.id, "name": p.name, "ingredients": p.ingredients} for p in Pizza.query.all()]
        return make_response(pizzas, 200)

class RestaurantPizzas(Resource):
    """Resource for handling requests to /restaurant_pizzas"""
    def post(self):
        """POST request to create a new restaurant pizza"""
        data = request.get_json()
        
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            
            return make_response(new_restaurant_pizza.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

# Adding resources to the API
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)