from flask import Flask
from demo import app, db
from databases.db import *
import config as custom_config

app = Flask(__name__)
app.config.from_object(custom_config)
db = SQLAlchemy(model_class=Base)
db.init_app(app)
app.config['DEBUG'] = True

def create_tables():
    "Create relational database tables"
    with app.app_context():
        db.create_all()


def drop_tables():
    "Drop all project relational database tables. THIS DELETES DATA"
    with app.app_context():
        db.drop_all()


def add_data_tables():
    with app.app_context():
        db.create_all()

        # Create expanded categories
        categories = [
            Category(name="Personal"),
            Category(name="Work"),
            Category(name="Study"),
            Category(name="Health"),
            Category(name="Shopping"),
            Category(name="Finance"),
            Category(name="Home"),
            Category(name="Travel"),
            Category(name="Social"),
            Category(name="Hobbies"),
            Category(name="Urgent"),
            Category(name="Projects")
        ]

        db.session.add_all(categories)
        db.session.commit()
        
        print("Database initialized with categories!")
        print("Categories created:", ", ".join([c.name for c in categories]))
        print("\nYou can now run 'python demo.py' and register a new user.")


if __name__ == '__main__':
    drop_tables()
    add_data_tables()