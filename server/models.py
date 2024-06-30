from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Defining naming convention for foreign keys
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initializing SQLAlchemy with the metadata
db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    """
    Restaurant model representing a restaurant in the database.
    """
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationship with RestaurantPizza, cascading deletes
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    
    # Association proxy to easily access pizzas through restaurant_pizzas
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Serialization rule to avoid recursive serialization
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    """
    Pizza model representing a pizza in the database.
    """
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationship with RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza')
    
    # Association proxy to easily access restaurants through restaurant_pizzas
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Serialization rule to avoid recursive serialization
    serialize_rules = ('-restaurant_pizzas.pizza',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    """
    RestaurantPizza model representing the many-to-many relationship
    between Restaurant and Pizza, with an additional price attribute.
    """
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))

    # Relationships with Restaurant and Pizza
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')

    # Serialization rules to avoid recursive serialization
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        """
        Validate that the price is between 1 and 30.
        """
        if not 1 <= price <= 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"