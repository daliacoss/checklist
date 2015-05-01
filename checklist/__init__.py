from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)
api = Api(app)

# app.jinja_env.trim_blocks = True
# app.jinja_env.lstrip_blocks = True

from checklist import views
