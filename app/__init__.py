import os

from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager, current_user
from flask_admin import Admin, expose, AdminIndexView


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" \
                                        % quote('Nguyenhoainam10')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 4
app.config["PRICE_SQR_COEF"] = 50
app.secret_key = 'GHFGH&*%^$^*(JHFGHF&Y*R%^$%$^&*TGYGJHFHGVJHGY'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["CUSTOMER_LIMIT"] = 3
db = SQLAlchemy(app=app)
login = LoginManager(app=app)

class DashboardView(AdminIndexView):
    def is_visible(self):
        # This view won't appear in the menu structure
        return False
    @expose('/')
    def index(self):
        if current_user.is_authenticated:
            return self.render('admin/index.html')
        return redirect('/admin/login')

Admin = Admin(app=app, name='QUẢN TRỊ KHÁCH SẠN',template_mode='bootstrap4', index_view=DashboardView())
