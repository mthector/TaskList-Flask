from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


class User(db.Model, UserMixin):
    """User accounts for authentication"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    email_hash = Column(String(256), unique=True, nullable=False)
    email_hint = Column(String(50), nullable=False)  # Shows partial email like "t***@example.com"
    password_hash = Column(String(256), nullable=False)
    
    tasks = relationship("Task", backref="user", lazy=True)
    
    def set_email(self, email):
        self.email_hash = generate_password_hash(email.lower())
        # Create email hint for display (e.g., "t***@example.com")
        parts = email.split('@')
        if len(parts) == 2:
            local = parts[0]
            domain = parts[1]
            if len(local) > 1:
                self.email_hint = local[0] + '***@' + domain
            else:
                self.email_hint = '***@' + domain
        else:
            self.email_hint = '***'
    
    def check_email(self, email):
        return check_password_hash(self.email_hash, email.lower())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """Categories of tasks"""
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return {u'<{self.__class__.__name__}: {self.id}>'.format(self=self)}


class Task(db.Model):
    """Tasks of our application"""
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text(255), nullable=False, default=None)
    due_date = Column(DateTime, nullable=True, default=None)
    completed = Column(Integer, default=0)  # 0 = pending, 1 = completed

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship("Category", backref="tasks")
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def countdown(self):
        return datetime.datetime.now() - self.due_date
