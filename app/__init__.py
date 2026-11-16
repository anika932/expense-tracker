from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()  # one shared database object


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from app.routes import bp
    app.register_blueprint(bp)

    from app.models import Category

    with app.app_context():
        db.create_all()  # creates tables if they don't exist

        if Category.query.count() == 0:
            defaults = {
                "Food": "swiggy,zomato,restaurant,cafe,dominos,pizza,grocery,bigbasket,blinkit",
                "Travel": "uber,ola,rapido,irctc,metro,petrol,fuel,flight,makemytrip",
                "Bills": "electricity,water bill,recharge,broadband,jio,airtel,gas,insurance",
                "Shopping": "amazon,flipkart,myntra,ajio,mall",
                "Entertainment": "netflix,hotstar,spotify,movie,bookmyshow,prime",
                "Other": "",
            }
            for name, kw in defaults.items():
                db.session.add(Category(name=name, keywords=kw))
            db.session.commit()

    return app