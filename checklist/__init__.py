from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)

# app.jinja_env.trim_blocks = True
# app.jinja_env.lstrip_blocks = True

from checklist import views, models
